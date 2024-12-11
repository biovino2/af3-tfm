#!/bin/bash
#SBATCH --job-name=alphafold3                       # Job name
#SBATCH --time=3:00:00                              # Time limit hrs:min:sec
#SBATCH --mem=16G                                   # Total memory
#SBATCH --partition=cpu                             # Partition (queue) name
#SBATCH --ntasks=1                                  # Number of tasks
#SBATCH --cpus-per-task=8                           # Number of CPU cores per task
#SBATCH --mail-type=ALL                             # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=benjamin.iovino@czbiohub.org    # Where to send mail

module load alphafold/3.0.0

input_json=$1
output_dir=$2
data_dir='/hpc/projects/data.science/benjamin.iovino/af3-tfm'

# Outputs json with MSA for proteins in input_json
alphafold \
    --json_path=${data_dir}/${input_json} \
    --output_dir=${data_dir}/${output_dir} \
    --norun_inference