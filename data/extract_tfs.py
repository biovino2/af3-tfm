"""
Extracts input TFs from the data and saves them in a separate directory.

Ben Iovino  12/05/24    CZ-Biohub
"""

import pandas as pd
import requests


def define_tfs() -> list[str]:
    """
    Manually define the TFs to be extracted.

    Returns:
        list[str]: List of TFs.
    """

    # TFs with direct motif evidence
    tfs = [
        "M01657_2.00",  # arid 6
        "M01679_2.00",  # kmt2cb
        "M01678_2.00",  # phf21ab
        "M01906_2.00",  # A6H8I1_DANRE
        "M01910_2.00",  # kdm2aa
        "M01909_2.00",  # kdm2ba
        "M02080_2.00",  # dharma
        "M02081_2.00",  # hoxd13a
        "M02082_2.00",  # si:dkey-43p13.5
        "M02079_2.00",  # vsx2
        "M02248_2.00",  # hsf2
        "M02384_2.00",  # myrf
        "M02393_2.00",  # nr2f2
        "M02425_2.00",  # pax2b
        "M03444_2.00",  # pax9
        "M02526_2.00",  # lin54
        "M02537_2.00",  # prkrira
        "M02536_2.00",  # prkrirb
    ]

    return tfs


def subset_tfs(tf_info: pd.DataFrame, tfs: list[str]) -> pd.DataFrame:
    """
    Subset the TF information dataframe to only include the TFs of interest.

    Args:
        tf_info (pd.DataFrame): TF information dataframe.
        tfs (list[str]): List of TFs to subset.

    Returns:
        pd.DataFrame: Subsetted TF dataframe.
    """

    tf_subset = tf_info[tf_info["Motif_ID"].isin(tfs)]
    tf_subset = tf_subset[["Motif_ID", "DBID", "TF_Name"]]

    return tf_subset


def fetch_protein_sequence(protein_id, format="fasta"):
    """
    Fetch protein sequence from Ensembl REST API.
    
    Args:
        protein_id (str): Ensembl protein ID (e.g., ENSP*).
        format (str): Output format ('fasta' or 'text').
    
    Returns:
        str: Protein sequence in the specified format.
    """

    url = f"https://rest.ensembl.org/sequence/id/{protein_id}"
    params = {"type": "protein", "multiple_sequences": "1"}
    headers = {"Content-Type": f"text/x-{format}"}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        seq = ''.join(response.text.split()[1:])  # remove header
        return seq
    else:
        return None


def get_seqs(tf_subset: pd.DataFrame):
    """
    Return dataframe with sequences from ensembl.

    Args:
        tf_subset (pd.DataFrame): Subsetted TF dataframe.

    Returns:
        pd.DataFrame: TF dataframe with sequences.
    """

    tf_subset["Sequence"] = tf_subset["DBID"].apply(fetch_protein_sequence)
    tf_subset = tf_subset[tf_subset["Sequence"].notna()]
    
    return tf_subset
    

def main():
    """
    """

    tfs = define_tfs()
    tf_info = pd.read_csv("data/cisbp/TF_Information.txt", sep="\t")
    tf_subset = subset_tfs(tf_info, tfs)
    tf_subset = get_seqs(tf_subset)
    tf_subset.to_csv("data/tf_subset.csv", index=False)
    

if __name__ == "__main__":
    main()
