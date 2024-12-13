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
        if key == "data_dir":
            config["slurm_output"] = f"{value}/slurm-%j.log"
            config["slurm_error"] = f"{value}/slurm-%j.log"
            config["output_dir"] = value
        else:
            config[key] = value

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
        slurm_script += f"#SBATCH --gpus={config["gpus"]}\n"
    if config["constraint"] != "None":
        slurm_script += f"#SBATCH --constraint={config["constraint"]}\n"

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

    path = "data/jobs/motifs_two"
    for job in os.listdir(path):

        # Update config with job specific information
        config = get_config(
            "src/config.yaml",
            data_dir=f"{path}/{job}",
            input_json=f"{path}/{job}/{job}.json",
            mail_user="benjamin.iovino@czbiohub.org",
            partition="cpu",
            run_inference=False,
        )

        # Submit slurm script
        slurm_script = generate_slurm_script(config)
        with open(f"{path}/{job}/run_af3.sh", "w") as f:
            f.write(slurm_script)
        sp.run(["sbatch", f"{path}/{job}/run_af3.sh"])


if __name__ == "__main__":
    main()
