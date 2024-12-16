"""
Generate json files for alphafold3 where each file contains a protein and it's motif.

Ben Iovino  12/10/24    CZ-Biohub
"""

import json
import os
import pandas as pd


def get_rev_comp(seq: str) -> str:
    """
    Returns the reverse complement of a DNA sequence.

    Args:
        seq (str): DNA sequence.

    Returns:
        str: Reverse complement of the input sequence.
    """

    return seq.replace('A', 't').replace('T', 'a').replace('C', 'g').replace('G', 'c').upper()[::-1]


def create_alphafold_job(name: str, sequences: list[dict]) -> dict:
    """
    Returns a JSON structure for an AlphaFold job.

    Args:
        name (str): Name of the job.
        sequences (list[dict]): List of sequences to predict.

    Returns:
        dict: JSON structure with protein, motif, and reverse compliment sequences.
    """

    job_data = {
        "name": name,
        "modelSeeds": [1],
        "sequences": [],
        "dialect": "alphafold3",
        "version": 1
    }
    
    # Add each sequence to the job data
    for seq in sequences:
        if 'protein' in seq:
            job_data["sequences"].append({
                "protein": {
                    "sequence": seq["protein"]["sequence"],
                    "id": seq["protein"]["id"]
                }
            })
        elif 'dna' in seq:
            job_data["sequences"].append({
                "dna": {
                    "sequence": seq["dna"]["sequence"],
                    "id": seq["dna"]["id"]
                }
            })

    return job_data


def get_json_data(tf_df: pd.DataFrame, jobs_name: str):
    """
    Save a JSON file for each TF.

    Args:
        tf_df (pd.DataFrame): TF dataframe.
        job_name (str): Name of the job set.
    """

    for _, row in tf_df.iterrows():
    
        # Get data from the row
        tf_name = row['TF_Name']
        seq = row['Sequence']
        motif = row['Motif']
        os.makedirs(f'data/jobs/{jobs_name}/{tf_name}', exist_ok=True)

        # Create and save JSON data
        sequences = [
            {"protein": {"sequence": seq, "id": "A"}},
            {"dna": {"sequence": motif, "id": "B"}},
            {"dna": {"sequence": get_rev_comp(motif), "id": "C"}},
        ]
        alphafold_job = create_alphafold_job(tf_name, sequences)
        with open(f'data/jobs/{jobs_name}/{tf_name}/{tf_name}.json', 'w') as f:
            json.dump(alphafold_job, f, indent=4)


def main():
    """
    """

    tf_df = pd.read_csv('data/tf_df.csv')
    get_json_data(tf_df, 'motifs')


if __name__ == "__main__":
    main()
