"""
Generate json files for alphafold3 where each file contains a protein and one of the motifs.
Each possible pair of protein and motif is generated (all-vs-all).

Ben Iovino  12/16/24    CZ-Biohub
"""

import json
import os
import pandas as pd
from make_json_motifs import get_rev_comp


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
        "modelSeeds": [1, 2, 3, 4, 5],
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
                    "id": seq["protein"]["id"],
                    "modifications": [],
                    "unpairedMsa": seq["protein"]["unpairedMsa"],
                    "pairedMsa": seq["protein"]["pairedMsa"],
                    "templates": seq["protein"]["templates"]
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

    # Get protein data from data/jobs/motifs
    for tf in tf_df['TF_Name']:

        # Load JSON file from jobs/motifs to get _data json
        with open(f'data/jobs/motifs_two/{tf}/{tf}_data.json', 'r') as f:
            data = json.load(f)
        protein = data['sequences'][0]
    
        # Generate a JSON for each motif
        for i, motif in enumerate(tf_df['Motif']):
            os.makedirs(f'data/jobs/{jobs_name}/{tf}_{i}', exist_ok=True)

            sequences = [
                protein,
                {"dna": {"sequence": motif, "id": "B"}},
                {"dna": {"sequence": get_rev_comp(motif), "id": "C"}},
            ]

            job_data = create_alphafold_job(f'{tf}_{i}', sequences)
            with open(f'data/jobs/{jobs_name}/{tf}_{i}/{tf}_{i}_data.json', 'w') as f:
                json.dump(job_data, f, indent=4)


def main():
    """
    """

    tf_df = pd.read_csv('data/tf_df.csv')
    get_json_data(tf_df, 'all-vs-all')


if __name__ == "__main__":
    main()
