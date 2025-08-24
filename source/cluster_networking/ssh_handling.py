"""
SSH handling and SLURM job management for cluster operations.
"""

import logging
import os
import time
from pathlib import Path
from typing import List, Tuple, Optional

import paramiko
from dotenv import load_dotenv

from utils.settings_manager import get_settings_manager

# Get logger for this module
logger = logging.getLogger(__name__)


class SSHConnectionError(Exception):
    """Custom exception for SSH connection issues."""
    pass


class SLURMJobError(Exception):
    """Custom exception for SLURM job submission issues."""
    pass


def validate_ssh_config() -> Tuple[str, int, str, str]:
    """
    Validate and return SSH configuration from settings.
    
    Returns:
        Tuple of (host, port, username, password)
        
    Raises:
        ValueError: If required settings are missing or invalid
    """
    settings_manager = get_settings_manager()
    settings = settings_manager.get_all_settings()
    
    # Get SSH settings from settings manager
    host = settings.get("ssh_host")
    if not host:
        raise ValueError("SSH host is not configured in settings")
    
    port = settings.get("ssh_port", 22)
    if not isinstance(port, int) or port <= 0 or port > 65535:
        raise ValueError("SSH port must be a valid port number (1-65535)")
    
    username = settings.get("ssh_user")
    if not username:
        raise ValueError("SSH user is not configured in settings")
    
    # Try to get password from environment first (for security), fallback to settings
    load_dotenv()
    password = os.getenv("SSH_PASS")
    if not password:
        password = settings.get("ssh_password", "")
        if not password:
            raise ValueError("SSH password is not configured. Set SSH_PASS environment variable or configure in settings")
    
    return host, port, username, password


def get_cluster_paths() -> Tuple[str, str, str]:
    """
    Get cluster-specific paths from settings.
    
    Returns:
        Tuple of (base_path, home_path, conda_env)
    """
    settings_manager = get_settings_manager()
    settings = settings_manager.get_all_settings()
    
    base_path = settings.get("cluster_base_path", "/proj/BV_data/")
    home_path = settings.get("cluster_home_path", "/home/vojtech.brejtr")
    conda_env = settings.get("cluster_conda_env", "DLC")
    
    return base_path, home_path, conda_env


def ssh_send_command(commands: List[str] | str, max_retries: Optional[int] = None, retry_delay: Optional[float] = None) -> bool:
    """
    Connect to remote host via SSH and send commands with retry logic.
    
    Args:
        commands: List of commands to execute on the remote host
        max_retries: Maximum number of connection attempts (if None, uses settings)
        retry_delay: Delay between retry attempts in seconds (if None, uses settings)
        
    Returns:
        bool: True if all commands were sent successfully, False otherwise
    """
    if not commands:
        logger.warning("No commands to send")
        return True
    
    if type(commands) is str:        
        commands = [commands]

    # Get retry settings from settings manager if not provided
    if max_retries is None or retry_delay is None:
        settings_manager = get_settings_manager()
        settings = settings_manager.get_all_settings()
        
        if max_retries is None:
            max_retries = settings.get("ssh_max_retries", 3)
        if retry_delay is None:
            retry_delay = settings.get("ssh_retry_delay", 5.0)
    
    # Ensure we have valid values
    assert max_retries is not None
    assert retry_delay is not None
    
    try:
        host, port, username, password = validate_ssh_config()
    except ValueError as e:
        logger.error(f"SSH configuration error: {e}")
        return False

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting SSH connection to {host}:{port} (attempt {attempt + 1}/{max_retries})")
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=30
            )
            
            logger.info(f"Successfully connected to {host}")
            
            successful_commands = 0
            for i, command in enumerate(commands):
                try:
                    logger.debug(f"Sending command {i+1}/{len(commands)} in background")
                    transport = client.get_transport()
                    if transport is not None:
                        channel = transport.open_session()
                        try:
                            bg_command = f"nohup {command} > /dev/null 2>&1 &"
                            channel.exec_command(bg_command)
                            successful_commands += 1
                        finally:
                            channel.close()
                    else:
                        logger.error("SSH transport is not available. Command not sent")
                        
                except Exception as cmd_error:
                    logger.error(f"Error executing command {i+1}: {cmd_error}")

            logger.info(f"Successfully sent {successful_commands}/{len(commands)} commands")
            return successful_commands == len(commands)
            
        except paramiko.AuthenticationException:
            logger.error(f"Authentication failed for user {username}")
            return False
        except paramiko.SSHException as ssh_error:
            logger.warning(f"SSH connection error (attempt {attempt + 1}): {ssh_error}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Connection failed")
                return False
        except Exception as e:
            logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Connection failed")
                return False
        finally:
            try:
                client.close()
            except:
                pass

    return False

def slurm_text_preprocessing(videos: List[str], keypoints: List[str], target_folder: str) -> List[str]:
    """
    Generate SLURM job scripts for video preprocessing.
    
    Args:
        videos: List of video file paths
        keypoints: List of keypoint file paths
        target_folder: Output folder for processed videos
        
    Returns:
        List of SLURM job script texts
    """
    _, home_path, conda_env = get_cluster_paths()
    
    # Get SLURM settings from settings manager
    settings_manager = get_settings_manager()
    settings = settings_manager.get_all_settings()
    
    cpus = settings.get("slurm_preprocessing_cpus", 1)
    memory = settings.get("slurm_preprocessing_memory", "8gb")
    time_limit = settings.get("slurm_preprocessing_time", "1-00:00:00")
    partition = settings.get("slurm_preprocessing_partition", "")
    
    # Get backend preprocessing settings
    boundary = settings.get("preprocessing_boundary", 100)
    output_width = settings.get("preprocessing_output_width", 1000)
    output_height = settings.get("preprocessing_output_height", 1000)
    
    def generate_text(video_file: str, corners: str) -> str:
        partition_line = f"#SBATCH --partition={partition}" if partition else ""
        
        return f"""#!/bin/bash
#SBATCH --job-name=PRC_BehaviorPipeline_Preprocessing_{Path(video_file).name}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={memory}
#SBATCH --time={time_limit}
{partition_line}
#SBATCH --output={home_path}/pipelines/app_preprocessing/logs_preprocessing/preprocessing_%j.log

module load Miniforge3/24.9.0-0
source /cvmfs/sys.sw.nudz/software/Miniforge3/24.9.0-0/bin/activate
conda activate {conda_env}

kinit -r 168h vojtech.brejtr@PCP.LF3.CUNI.CZ < {home_path}/Desktop/log

cd {home_path}/pipelines/app_preprocessing/

python preprocessing.py --video_path {video_file} --corners '{corners}' --folder_out {target_folder} --boundary {boundary} --output_width {output_width} --output_height {output_height}
"""

    slurm_texts = [generate_text(v, k) for v, k in zip(videos, keypoints)]
    return slurm_texts


def slurm_text_tracking(videos: List[str], target_folder: str, max_concurrent: int = 4) -> List[str]:
    chunks = [[] for _ in range(max_concurrent)]
    for i, video in enumerate(videos):
        chunks[i % max_concurrent].append(video)

    _, home_path, conda_env = get_cluster_paths()
    
    # Get SLURM settings from settings manager
    settings_manager = get_settings_manager()
    settings = settings_manager.get_all_settings()
    
    cpus = settings.get("slurm_tracking_cpus", 4)
    memory = settings.get("slurm_tracking_memory", "16gb")
    time_limit = settings.get("slurm_tracking_time", "1-00:00:00")
    partition = settings.get("slurm_tracking_partition", "PipelineProdGPU")
    
    # Get DLC backend settings
    config_path = settings.get("dlc_config_path", "/home/vojtech.brejtr/projects/DLC_Basler/NPS-Basler-2025-02-19/config.yaml")
    video_type = settings.get("dlc_video_type", ".mp4")
    shuffle = settings.get("dlc_shuffle", 1)
    batch_size = settings.get("dlc_batch_size", 16)
    save_as_csv = settings.get("dlc_save_as_csv", True)
    
    partition_line = f"#SBATCH --partition={partition}" if partition else ""
    
    def generate_text(chunk: List[str]) -> str:
        return f"""
            #!/bin/bash
            #SBATCH --job-name=PRC_BehaviorPipeline_Tracking
            # #SBATCH --ntasks=1
            #SBATCH --cpus-per-task={cpus}
            #SBATCH --gres=gpu:1
            {partition_line}
            #SBATCH --mem={memory}
            #SBATCH --time={time_limit}
            #SBATCH --output={home_path}/pipelines/app_preprocessing/logs_tracking/tracking_array_%A_%a.log

            module load Miniforge3/24.9.0-0
            source /cvmfs/sys.sw.nudz/software/Miniforge3/24.9.0-0/bin/activate
            conda activate {conda_env}

            kinit -r 168h vojtech.brejtr@PCP.LF3.CUNI.CZ < {home_path}/Desktop/log

            cd {home_path}/pipelines/app_preprocessing/

            python extract_pose.py --config_path {config_path} --video_path '{":::".join(chunk)}' --video_type {video_type} --out_folder {target_folder} --shuffle {shuffle} --batch_size {batch_size} --save_as_csv {"1" if save_as_csv else "0"} > /dev/null 2>&1
            """
            
    commands = [generate_text(chunk) for chunk in chunks if chunk]
    return commands