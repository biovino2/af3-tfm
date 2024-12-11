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
        if os.path.exists(f"{path}/{job}/{job}_data.json"):
            print(f"data json already exists for {job}")
            continue
        sp.run(["sbatch", "src/no_inf.bash", f"{path}/{job}/{job}.json", f"{path}"])


if __name__ == "__main__":
    main()
