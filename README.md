# Transcription Factor-Motif Binding with AlphaFold3
Pilot experiments to determine accuracy of TF-Motif binding using AlphaFold3.

## Data
Downloaded all Danio rerio TFs from CisBP (https://cisbp.ccbr.utoronto.ca/bulk.php). TFs of interest can be extracted with `data/extract_tfs.py` and their canonical sequences downloaded from ensembl. AlphaFold3 requires json files as input, which can be prepared with `data/make_json.py` where each TF and it's corresponding motif are prepared.

## Running AlphaFold3
AlphaFold3 has two steps as outlined below (taken from their GitHub: https://github.com/google-deepmind/alphafold3)

1. --run_data_pipeline (defaults to true): whether to run the data pipeline, i.e. genetic and template search. This part is CPU-only, time consuming and could be run on a machine without a GPU.
2. --run_inference (defaults to true): whether to run the inference. This part requires a GPU.

We separate these two steps because we will reuse the same TF for predictions with various motifs, meaning we only need to run the data pipeline once (also a time-consuming step). The data pipeline can be run for all prepared json files with `src/no_inf.py`. Predict folding with `src/fold.py`.