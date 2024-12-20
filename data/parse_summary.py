"""
Parses AlphaFold3 summary confidences file to find confidence scores.

Ben Iovino  12/16/24    CZ-Biohub
"""

import json
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns


def load_results(jobs_dir: str):
    """
    Load the ipTM scores for the TF-motif predictions.

    Args:
        jobs_dir (str): The directory containing the job folders.

    Returns:
        dict: The ipTM scores for each TF-motif prediction.
    """

    results = {}
    for job in os.listdir(jobs_dir):
        if job.startswith('kdm2ab') or job.startswith('kdm2bb'):
            continue
        result_file = f'{jobs_dir}/{job}/{job}_summary_confidences.json'
        with open(result_file) as f:
            data = json.load(f)
        results[job] = data['iptm']

    return results


def graph_motifs(jobs_dir: str):
    """
    Graph the ipTM scores for the TF-motif predictions.

    Args:
        jobs_dir (str): The directory containing the job folders.
    """

    results = load_results(jobs_dir)

    # Graph results
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(5, 5))
    sns.boxplot(data=results, ax=ax)
    plt.xticks(rotation=90)
    plt.ylabel('Confidence')
    plt.title('ipTM Confidence Scores')
    plt.hlines(0.6, -1, 1, colors='r', linestyles='dashed')
    plt.hlines(0.8, -1, 1, colors='g', linestyles='dashed')
    plt.savefig('data/iptm_scores.png')


def graph_all_vs_all(jobs_dir: str):
    """
    Graph the ipTM scores for all TFs against all motifs.

    Args:
        jobs_dir (str): The directory containing the job folders.
    """

    results = load_results(jobs_dir)

    # Order dict first by tf_order, then by job number
    tf_df = pd.read_csv('data/tf_df_updated.csv')
    tf_order = tf_df['TF_Name'].tolist()
    sorted_keys = sorted(
        results.keys(),
        key=lambda k: (tf_order.index(k.split("_")[0]), int(k.split("_")[1]))
    )

    # Make dataframe where each column is 0-17 (a motif) and each row is a TF
    cols = [f'{i}' for i in range(16)]
    df = pd.DataFrame(columns=cols)
    for key in sorted_keys:
        tf = key.split("_")[0]
        motif = key.split("_")[1]
        df.loc[tf, motif] = float(results[key])
    df.drop(df.columns[4], axis=1, inplace=True)
    df.drop(df.columns[6], axis=1, inplace=True)

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
    plt.savefig('data/all_vs_all-5seed.png', bbox_inches='tight')


def graph_padding(jobs_dir: list[str]):
    """
    Graph ipTM scores for all of the padding jobs.

    Args:
        jobs_dir (list): The list of directories containing the job folders.
    """

    fig, ax = plt.subplots(figsize=(5, 5))
    for job in jobs_dir:
        results = load_results(job)

        # Get median, mean, and std of the values in the dict
        median = pd.Series(results).median()
        std = pd.Series(results).std()

        # Add to plot
        ax.errorbar(
            job.split('_')[-1],
            median,
            yerr=std,
            fmt='o',
            color='black',
            capsize=5
            )

        # Add legend with dots for median
        ax.legend(
            ['Median'],
            loc='upper right',
            fontsize='small',
            )
        
    plt.ylabel('Confidence')
    plt.xlabel('Padding')
    plt.title('ipTM Confidence Scores')
    plt.savefig('data/padding_scores.png')


def main():
    """
    """

    padding_dirs = [
        'data/jobs/padding_2',
        'data/jobs/padding_4',
        'data/jobs/padding_6',
        'data/jobs/padding_8',
        'data/jobs/padding_10',
        'data/jobs/padding_12'
        ]
    graph_padding(padding_dirs)

    graph_motifs('data/jobs/motifs_5seed')


if __name__ == '__main__':
    main()
