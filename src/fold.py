"""
Submit slurm jobs for each sample in a directory.

Ben Iovino  12/10/24    CZ-Biohub
"""

import os
import subprocess as sp


def main():
    """
    """

    path = "data/jobs/motifs"
    for job in os.listdir(path):
        if not os.path.exists(f"{path}/{job}/{job}_data.json"):
            print(f"no data json exists for {job}")
            continue
        if os.path.exists(f"{path}/{job}/{job}/"):
            print(f"alphafold directory already exists for {job}")
            continue
        sp.run(["sbatch", "src/fold.bash", f"{path}/{job}/{job}_data.json", f"{path}/{job}"])


if __name__ == "__main__":
    main()