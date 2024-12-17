"""
Parses AlphaFold3 summary confidences file to find confidence scores.

Ben Iovino  12/16/24    CZ-Biohub
"""

import json
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns


def graph_motifs():
    """
    Graph the ipTM scores for the TF-motif predictions.
    """

    path = 'data/jobs/motifs_two'
    results = {}
    for job in os.listdir(path):
        result_file = f'{path}/{job}/{job}_summary_confidences.json'
        with open(result_file) as f:
            data = json.load(f)
        results[job] = data['iptm']

    # Graph results
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(5, 5))
    sns.boxplot(data=results, ax=ax)
    plt.xticks(rotation=90)
    plt.ylabel('Confidence')
    plt.title('ipTM Confidence Scores')
    plt.hlines(0.6, -1, 1, colors='r', linestyles='dashed')
    plt.hlines(0.8, -1, 1, colors='g', linestyles='dashed')
    plt.savefig('data/iptm_scores.pdf')


def graph_all_vs_all():
    """
    Graph the ipTM scores for all TFs against all motifs.
    """

    path = 'data/jobs/all-vs-all-5seed'
    results = {}
    for job in os.listdir(path):
        result_file = f'{path}/{job}/{job}_summary_confidences.json'
        with open(result_file) as f:
            data = json.load(f)
        results[job] = data['iptm']

    # Order dict first by tf_order, then by job number
    tf_df = pd.read_csv('data/tf_df.csv')
    tf_order = tf_df['TF_Name'].tolist()
    sorted_keys = sorted(
        results.keys(),
        key=lambda k: (tf_order.index(k.split("_")[0]), int(k.split("_")[1]))
    )

    # Make dataframe where each column is 0-17 (a motif) and each row is a TF
    cols = [f'{i}' for i in range(18)]
    df = pd.DataFrame(columns=cols)
    for key in sorted_keys:
        tf = key.split("_")[0]
        motif = key.split("_")[1]
        df.loc[tf, motif] = float(results[key])

    df = df.apply(pd.to_numeric, errors='coerce')

    # Update columns to be motif strings
    motifs = tf_df['Motif'].tolist()
    df.columns = motifs
    
    # Graph heatmap of df
    plt.figure(figsize=(12, 5))
    sns.heatmap(df, cmap='viridis')
    plt.ylabel('TF')
    plt.xlabel('Motif')
    plt.title('ipTM Confidence Scores')
    for i in range(18):  # Border around diagonal squares
        plt.gca().add_patch(plt.Rectangle((i, i), 1, 1, fill=False, edgecolor='black', lw=2))
    plt.savefig('data/all_vs_all-5seed.pdf', bbox_inches='tight')


def main():
    """
    """

    graph_all_vs_all()


if __name__ == '__main__':
    main()
