"""
Run AlphaFold3 for a given JSON file.

Ben Iovino  12/13/24    CZ-Biohub
"""

import os
import subprocess as sp
import yaml


def get_config(config_file: str, **kwargs) -> dict:
    """
    Read the configuration file and return the configuration dictionary.

    Args:
        config_file (str): The path to the configuration file.
        **kwargs: The arguments to update the configuration dictionary.

    Returns:
        dict: The configuration dictionary.
    """

    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # Update config based on kwargs
    for key, value in kwargs.items():
        config[key] = value

    return config


def cpu_config(path: str, job: str) -> dict:
    """
    Returns config for a CPU job.

    Args:
        path (str): The path to the JSON file.
        job (str): The job name.

    Returns:
        dict: The configuration dictionary.
    """

    config = get_config(
            "src/config.yaml",
            output_dir=f"{path}",
            input_json=f"{path}/{job}/{job}.json",
            mail_user="benjamin.iovino@czbiohub.org",
            slurm_output=f"{path}/{job}/slurm-%j.log",
            slurm_error=f"{path}/{job}/slurm-%j.log",
            partition="cpu",
            run_inference=False,
            time="3:00:00",
        )

    return config


def gpu_config(path: str, job: str, constraint: str = "None") -> dict:
    """
    Returns config for a GPU job.

    Args:
        path (str): The path to the JSON file.
        job (str): The job name.
        constraint (str): The GPU constraint.

    Returns:
        dict: The configuration dictionary.
    """

    # Check for _data json file
    if os.path.exists(f"{path}/{job}/{job}_data.json"):
        input_json = f"{path}/{job}/{job}_data.json"
        run_data_pipeline = False
    else:
        input_json = f"{path}/{job}/{job}.json"
        run_data_pipeline = True

    config = get_config(
            "src/config.yaml",
            output_dir=f"{path}",
            input_json=input_json,
            mail_user="benjamin.iovino@czbiohub.org",
            slurm_output=f"{path}/{job}/slurm-%j.log",
            slurm_error=f"{path}/{job}/slurm-%j.log",
            partition="gpu",
            run_data_pipeline=run_data_pipeline,
            time="3:00:00"
        )
    
    # Specific GPU options
    if constraint != "None":
        config["constraint"] = constraint

    return config


def generate_slurm_script(config: dict[str]) -> str:
    """
    Generate a slurm script for AlphaFold3.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        str: The slurm script.
    """

    slurm_script = f"""#!/bin/bash
#SBATCH --job-name=alphafold3
#SBATCH --time={config["time"]}
#SBATCH --mem={config["mem"]}
#SBATCH --partition={config["partition"]}
#SBATCH --ntasks={config["ntasks"]}
#SBATCH --cpus-per-task={config["cpus_per_task"]}
#SBATCH --mail-type={config["mail_type"]}
#SBATCH --mail-user={config["mail_user"]}
#SBATCH --output={config["slurm_output"]}
#SBATCH --error={config["slurm_error"]}
"""
    
    # GPU specific options
    if config["partition"] == "gpu":
        slurm_script += f"#SBATCH --gpus={config['gpus']}\n"
    if config["constraint"] != "None":
        slurm_script += f"#SBATCH --constraint={config['constraint']}\n"

    slurm_script += f"""
module load alphafold/3.0.0
alphafold \
--json_path={config["input_json"]} \
--output_dir={config["output_dir"]} \
"""
    
    # Optional AF3 flags to separate steps
    if config["run_inference"] is False:
        slurm_script += "--run_inference=false"
    if config["run_data_pipeline"] is False:
        slurm_script += "--run_data_pipeline=false"
    
    return slurm_script


def main():
    """
    """

    partition = 'gpu'
    path = "data/jobs/motifs_two"
    for job in os.listdir(path):

        # Config based on cpu/gpu
        if partition == 'cpu':
            config = cpu_config(path, job)
        if partition == 'gpu':
            config = gpu_config(path, job)

        # Submit slurm script
        slurm_script = generate_slurm_script(config)
        with open(f"{path}/{job}/run_af3_{partition}.sh", "w") as f:
            f.write(slurm_script)
        sp.run(["sbatch", f"{path}/{job}/run_af3_{partition}.sh"])


if __name__ == "__main__":
    main()
