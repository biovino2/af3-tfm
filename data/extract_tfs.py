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
    

def fetch_canonical_protein(gene_id) -> str:
    """
    Fetch the canonical protein sequence for a given Ensembl gene ID.
    
    Args:
        gene_id (str): Ensembl gene ID (ENSG*).
    
    Returns:
        str: Canonical protein sequence in FASTA format.
    """

    # Step 1: Get the canonical transcript
    url_lookup = f"https://rest.ensembl.org/lookup/id/{gene_id}"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url_lookup, headers=headers)
    
    if response.status_code != 200:
        return None
    
    data = response.json()
    canonical_transcript = data.get("canonical_transcript")
    canonical_transcript = canonical_transcript.split(".")[0]
    
    if not canonical_transcript:
        raise Exception(f"No canonical transcript found for gene ID: {gene_id}")
    
    # Step 2: Get the protein sequence for the canonical transcript
    url_sequence = f"https://rest.ensembl.org/sequence/id/{canonical_transcript}"
    params = {"type": "protein"}
    headers = {"Content-Type": "application/json"}
    response_sequence = requests.get(url_sequence, headers=headers, params=params)
    
    if response_sequence.status_code == 200:
        return response_sequence.json()['seq']
    else:
        return None


def get_seqs(tf_df: pd.DataFrame) -> pd.DataFrame:
    """
    Return dataframe with sequences from ensembl.

    Args:
        tf_subset (pd.DataFrame): Subsetted TF dataframe.

    Returns:
        pd.DataFrame: TF dataframe with sequences.
    """

    tf_df["Sequence"] = tf_df["DBID"].apply(fetch_canonical_protein)
    tf_df = tf_df[tf_df["Sequence"].notna()]
    
    return tf_df


def get_motifs(tf_df: pd.DataFrame) -> pd.DataFrame:
    """
    Return dataframe with motifs from cisbp PWMs.

    Args:
        tf_df (pd.DataFrame): TF dataframe.

    Returns:
        pd.DataFrame: TF dataframe with motifs.
    """

    for tf in tf_df["Motif_ID"]:
        pwm = pd.read_csv(f"data/cisbp/pwms_all_motifs/{tf}.txt", sep="\t")

        # Take base with highest probability
        pwm.drop(columns=["Pos"], inplace=True)
        motif = pwm.idxmax(axis=1).str.cat()
        tf_df.loc[tf_df["Motif_ID"] == tf, "Motif"] = motif

    return tf_df
    

def main():
    """
    """

    tfs = define_tfs()
    tf_info = pd.read_csv("data/cisbp/TF_Information.txt", sep="\t")
    tf_df = subset_tfs(tf_info, tfs)
    tf_df = get_seqs(tf_df)
    tf_df = get_motifs(tf_df)
    tf_df.to_csv("data/tf_df.csv", index=False)
    

if __name__ == "__main__":
    main()
