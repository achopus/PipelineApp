import paramiko
import os
from pathlib import Path
from dotenv import load_dotenv

def ssh_send_command(commands: list[str]):
    """
    Connect to remote host via SSH and send commands without waiting for each to finish.
    """
    from dotenv import load_dotenv
    import os
    import paramiko

    load_dotenv()
    host = os.getenv("SSH_HOST", "sup200.ad.nudz.cz")
    port = int(os.getenv("SSH_PORT", "22"))
    username = os.getenv("SSH_USER")
    password = os.getenv("SSH_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=host, port=port, username=username, password=password)

        for command in commands:
            bg_command = f"{command} &"
            print(f"Sending command in background: {bg_command}")
            transport = client.get_transport()
            if transport is not None:
                channel = transport.open_session()
                channel.exec_command(bg_command)  # no .read() — don't block
            else:
                print("Error: SSH transport is not available. Command not sent.")

        print("All commands sent.")

    finally:
        client.close()


def slurm_text_preprocessing(project_folder: str, videos: list[str], keypoints: list[str], target_folder: str) -> list[str]:
    def generate_text(video_file: str, corners: str) -> str:
        return f"""
        #!/bin/bash
        #SBATCH --job-name=PRC_BehaviorPipeline_Preprocessing_{Path(video_file).name}
        #SBATCH --ntasks=1
        #SBATCH --cpus-per-task=1
        #SBATCH --mem=8gb
        #SBATCH --time=1-00:00:00
        #SBATCH --output=logs/preprocessing_%j.log

        module load Miniforge3/24.9.0-0
        source /cvmfs/sys.sw.nudz/software/Miniforge3/24.9.0-0/bin/activate
        conda activate DLC

        kinit vojtech.brejtr@PCP.LF3.CUNI.CZ < /home/vojtech.brejtr/Desktop/log

        cd /home/vojtech.brejtr/pipelines/app_preprocessing/
        
        python preprocessing.py --video_path {video_file} --corners {f"'{corners}'"} --folder_out {target_folder}
        """

    slurm_texts = [generate_text(v, k) for v, k in zip(videos, keypoints)]
    return slurm_texts

def slurm_text_tracking(project_folder: str, videos: list[str], target_folder: str) -> list[str]:
    def generate_text(video_file: str):
        return f"""
        #!/bin/bash
        #SBATCH --job-name=PRC_BehaviorPipeline_Tracking_{Path(video_file).name}
        #SBATCH --ntasks=1
        #SBATCH --cpus-per-task=1
        #SBATCH --partition=PipelineProdGPU
        #SBATCH --mem=16gb
        #SBATCH --time=1-00:00:00
        #SBATCH --output=logs/tracking_%j.log
        
        module load Miniforge3/24.9.0-0
        source /cvmfs/sys.sw.nudz/software/Miniforge3/24.9.0-0/bin/activate
        conda activate DLC

        kinit vojtech.brejtr@PCP.LF3.CUNI.CZ < /home/vojtech.brejtr/Desktop/log

        cd /home/vojtech.brejtr/pipelines/app_preprocessing/

        python extract_pose.py --video_path {video_file} --out_folder {target_folder}
        """
        
    slurm_texts = [generate_text(v) for v in videos]
    return slurm_texts


if __name__ == "__main__":
    project_folder = "test_project"
    videos = ["video1.mp4", "video2.mp4"]
    points = ["[[1, 2], [3, 4], [5, 6], [7, 8]]", "[[1, 2], [3, 4], [5, 6], [7, 8]]"]
    target_folder = "test_target"
    
    commands = slurm_text_preprocessing(project_folder, videos, points, target_folder)
    
    ssh_send_command(commands)