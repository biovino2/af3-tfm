"""
Parses slurm output file for job information.

Ben Iovino  12/16/24    CZ-Biohub
"""

import matplotlib.pyplot as plt
import os
import pandas as pd
import re
import seaborn as sns
import subprocess as sp


def parse_seff(file: str) -> tuple:
    """
    Parse the seff output for job information.

    Args:
        file (str): The path to the slurm log file.

    Returns:
        tuple (str, str): The time and memory used
    """

    # Run seff for job id
    regex = r"[0-9]+"
    job_id = re.search(regex, file).group()
    out = sp.run(f"seff {job_id}", capture_output=True, shell=True)
    out = out.stdout.decode()

    # Search for time and memory
    regex = r"(?<=Job Wall-clock time: )\d{2}:\d{2}:\d{2}"
    time = re.search(regex, out).group()
    regex = r"(?<=Memory Utilized: )\d+(\.\d+)? (GB|MB)"
    memory = re.search(regex, out).group()

    # Convert time to minutes
    h, m, s = time.split(':')
    time = round(int(h)*60 + int(m) + int(s)/60, 2)

    # Convert memory to GB (if necessary)
    memory = memory.split(' ')
    if memory[1] == 'MB':
        memory = round(float(memory[0]) / 1024, 2)
    else:
        memory = float(memory[0])

    return time, memory


def parse_slurm_log(slurm_filepath: str) -> tuple:
    """
    For an AlphaFold3 job, parse the slurm log file for job information.

    Args:
        slurm_filepath (str): The path to the slurm log file.

    Returns:
        tuple (str, str, str): The partition, time, and memory used.
    """

    partition = ''
    with open(slurm_filepath, "r") as f:
        lines = f.readlines()
    
    # Search for partition type
    regex1 = r"Running data pipeline...\n"
    regex2 = r"Running model inference for seed 1...\n"
    for line in lines:
        if re.search(regex1, line):
            partition = 'cpu'
            break
        if re.search(regex2, line):
            partition = 'gpu'
            break

    # Parse seff output
    slurm_filename = slurm_filepath.split("/")[-1]
    time, memory = parse_seff(slurm_filename)
    
    return partition, time, memory


def parse_logs(path: str) -> dict:
    """
    Parse all slurm logs in a directory.

    Args:
        path (str): The path to the directory.

    Returns:
        dict: A dictionary of job information.
    """

    results = {}
    for job in os.listdir(path):
        results[job] = {}
        
        # Parse each slurm log (can be multiple)
        slurm_files = [f for f in os.listdir(f"{path}/{job}") if "slurm" in f]
        for file in slurm_files:
            partition, time, memory = parse_slurm_log(f"{path}/{job}/{file}")
            results[job][partition] = {
                "time": time,
                "memory": memory
            }

    return results


def graph_results(results: dict):
    """
    """

    # Get TF lengths
    tf_lengths = []
    tf_df = pd.read_csv("data/tf_df.csv")
    for tf in results:
        seq = tf_df[tf_df['TF_Name'] == tf]['Sequence'].values[0]
        tf_lengths.append(len(seq))

    # Graph all CPU results
    cpu_times = []
    cpu_memory = []
    for job in results:
        if 'cpu' in results[job]:
            cpu_times.append(results[job]['cpu']['time'])
            cpu_memory.append(results[job]['cpu']['memory'])

    # Graph all GPU results
    gpu_times = []
    gpu_memory = []
    for job in results:
        if 'gpu' in results[job]:
            gpu_times.append(results[job]['gpu']['time'])
            gpu_memory.append(results[job]['gpu']['memory'])

    # Plot the run times
    plt.figure(figsize=(8, 4), dpi=100)
    sns.scatterplot(x=tf_lengths, y=cpu_times, label='MSA Generation (8 CPUs)')
    sns.scatterplot(x=tf_lengths, y=gpu_times, label='Structure Inference (1 GPU)')
    plt.xlabel('Protein Sequence Length')
    plt.ylabel('Time (minutes)')
    plt.title('AlphaFold3 Runtime')
    plt.legend()
    plt.savefig('data/runtime.pdf')

    # Plot the memory usage
    plt.figure(figsize=(8, 4), dpi=100)
    sns.scatterplot(x=tf_lengths, y=cpu_memory, label='MSA Generation (8 CPUs)')
    sns.scatterplot(x=tf_lengths, y=gpu_memory, label='Structure Inference (1 GPU)')
    plt.xlabel('Protein Sequence Length')
    plt.ylabel('Memory (GB)')
    plt.title('AlphaFold3 Memory Usage')
    plt.legend()
    plt.savefig('data/memory.pdf')


def main():
    """
    """

    path = "data/jobs/motifs_two"
    results = parse_logs(path)
    graph_results(results)


if __name__ == "__main__":
    main()
