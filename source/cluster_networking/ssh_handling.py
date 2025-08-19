"""
SSH handling and SLURM job management for cluster operations.
"""

import os
import time
from pathlib import Path
from typing import List, Optional, Tuple

import paramiko
from dotenv import load_dotenv


class SSHConnectionError(Exception):
    """Custom exception for SSH connection issues."""
    pass


class SLURMJobError(Exception):
    """Custom exception for SLURM job submission issues."""
    pass


def validate_ssh_config() -> Tuple[str, int, str, str]:
    """
    Validate and return SSH configuration from environment variables.
    
    Returns:
        Tuple of (host, port, username, password)
        
    Raises:
        ValueError: If required environment variables are missing or invalid
    """
    load_dotenv()
    
    host = os.getenv("SSH_HOST")
    if not host:
        raise ValueError("SSH_HOST environment variable is required")
    
    try:
        port = int(os.getenv("SSH_PORT", "22"))
    except ValueError:
        raise ValueError("SSH_PORT must be a valid integer")
    
    username = os.getenv("SSH_USER")
    if not username:
        raise ValueError("SSH_USER environment variable is required")
    
    password = os.getenv("SSH_PASS")
    if not password:
        raise ValueError("SSH_PASS environment variable is required")
    
    return host, port, username, password


def get_cluster_paths() -> Tuple[str, str, str]:
    """
    Get cluster-specific paths from environment variables.
    
    Returns:
        Tuple of (base_path, home_path, conda_env)
    """
    load_dotenv()
    
    base_path = os.getenv("CLUSTER_BASE_PATH", "/proj/BV_data/")
    home_path = os.getenv("CLUSTER_HOME_PATH", "/home/vojtech.brejtr")
    conda_env = os.getenv("CLUSTER_CONDA_ENV", "DLC")
    
    return base_path, home_path, conda_env


def ssh_send_command(commands: List[str], max_retries: int = 3, retry_delay: float = 5.0) -> bool:
    """
    Connect to remote host via SSH and send commands with retry logic.
    
    Args:
        commands: List of commands to execute on the remote host
        max_retries: Maximum number of connection attempts
        retry_delay: Delay between retry attempts in seconds
        
    Returns:
        bool: True if all commands were sent successfully, False otherwise
    """
    if not commands:
        print("No commands to send.")
        return True
    
    try:
        host, port, username, password = validate_ssh_config()
    except ValueError as e:
        print(f"SSH configuration error: {e}")
        return False

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for attempt in range(max_retries):
        try:
            print(f"Attempting SSH connection to {host}:{port} (attempt {attempt + 1}/{max_retries})")
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=30
            )
            
            print(f"Successfully connected to {host}")
            
            successful_commands = 0
            for i, command in enumerate(commands):
                try:
                    print(f"Sending command {i+1}/{len(commands)} in background")
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
                        print("Error: SSH transport is not available. Command not sent.")
                        
                except Exception as cmd_error:
                    print(f"Error executing command {i+1}: {cmd_error}")

            print(f"Successfully sent {successful_commands}/{len(commands)} commands")
            return successful_commands == len(commands)
            
        except paramiko.AuthenticationException:
            print(f"Authentication failed for user {username}")
            return False
        except paramiko.SSHException as ssh_error:
            print(f"SSH connection error (attempt {attempt + 1}): {ssh_error}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Connection failed.")
                return False
        except Exception as e:
            print(f"Unexpected error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Connection failed.")
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
    
    def generate_text(video_file: str, corners: str) -> str:
        return f"""#!/bin/bash
#SBATCH --job-name=PRC_BehaviorPipeline_Preprocessing_{Path(video_file).name}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH --time=1-00:00:00
#SBATCH --output={home_path}/pipelines/app_preprocessing/logs_preprocessing/preprocessing_%j.log

module load Miniforge3/24.9.0-0
source /cvmfs/sys.sw.nudz/software/Miniforge3/24.9.0-0/bin/activate
conda activate {conda_env}

kinit vojtech.brejtr@PCP.LF3.CUNI.CZ < {home_path}/Desktop/log

cd {home_path}/pipelines/app_preprocessing/

python preprocessing.py --video_path {video_file} --corners '{corners}' --folder_out {target_folder}
"""

    slurm_texts = [generate_text(v, k) for v, k in zip(videos, keypoints)]
    return slurm_texts


def slurm_text_tracking(videos: List[str], target_folder: str) -> List[str]:
    """
    Generate SLURM job scripts for video tracking.
    
    Args:
        videos: List of video file paths
        target_folder: Output folder for tracking results
        
    Returns:
        List of SLURM job script texts
    """
    _, home_path, conda_env = get_cluster_paths()
    
    def generate_text(video_file: str) -> str:
        return f"""#!/bin/bash
#SBATCH --job-name=PRC_BehaviorPipeline_Tracking_{Path(video_file).name}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --partition=PipelineProdGPU
#SBATCH --mem=16gb
#SBATCH --time=1-00:00:00
#SBATCH --output={home_path}/pipelines/app_preprocessing/logs_tracking/tracking_%j.log

module load Miniforge3/24.9.0-0
source /cvmfs/sys.sw.nudz/software/Miniforge3/24.9.0-0/bin/activate
conda activate {conda_env}

kinit vojtech.brejtr@PCP.LF3.CUNI.CZ < {home_path}/Desktop/log

cd {home_path}/pipelines/app_preprocessing/

python extract_pose.py --video_path {video_file} --out_folder {target_folder} > /dev/null 2>&1
"""
        
    slurm_texts = [generate_text(v) for v in videos]
    return slurm_texts
