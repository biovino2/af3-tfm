"""
Generate json files for alphafold3 where each file contains a protein and it's motif, plus padding.

Ben Iovino  12/17/24    CZ-Biohub
"""

import json
import os
import pandas as pd
from make_json_motifs import get_rev_comp
from make_json_ava import create_alphafold_job


def add_padding(motif: str, padding: int) -> str:
    """
    Add padding to the motif.

    Args:
        motif (str): The motif to pad.
        padding (int): The number of nucleotides to pad the motif with.

    Returns:
        str: The padded motif.
    """

    return 'A'*padding + motif + 'A'*padding


def get_json_data(tf_df: pd.DataFrame, jobs_name: str, padding: int):
    """
    Save a JSON file for each TF.

    Args:
        tf_df (pd.DataFrame): TF dataframe.
        job_name (str): Name of the job set.
        padding (int): The number of nucleotides to pad the motif with.
    """

    for _, row in tf_df.iterrows():
    
        # Get data from the row
        tf_name = row['TF_Name']
        motif = row['Motif']
        os.makedirs(f'data/jobs/{jobs_name}/{tf_name}', exist_ok=True)

        # Load JSON file from jobs/motifs to get _data json
        with open(f'data/jobs/motifs_two/{tf_name}/{tf_name}_data.json', 'r') as f:
            data = json.load(f)
        protein = data['sequences'][0]

        # Pad motif if necessary
        if padding > 0:
            motif = add_padding(motif, padding)

        sequences = [
            protein,
            {"dna": {"sequence": motif, "id": "B"}},
            {"dna": {"sequence": get_rev_comp(motif), "id": "C"}},
        ]

        job_data = create_alphafold_job(tf_name, sequences)
        with open(f'data/jobs/{jobs_name}/{tf_name}/{tf_name}_data.json', 'w') as f:
            json.dump(job_data, f, indent=4)


def main():
    """
    """

    padding = 2
    tf_df = pd.read_csv('data/tf_df.csv')
    get_json_data(tf_df, f"padding_{padding}", padding)


if __name__ == "__main__":
    main()
