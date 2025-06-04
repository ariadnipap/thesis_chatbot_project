import os
import json
import pandas as pd
import re

# Path to your evaluation results
EVAL_DIR = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/evaluation_with_preprocessing/"

def parse_config(fname):
    match = re.match(r"evaluation_results_(\d+)_([0-9.]+)_(chunked_\d+_\d+|no_chunking)\.json", fname)
    if match:
        return int(match.group(1)), float(match.group(2)), match.group(3)
    return None

records = []
for fname in os.listdir(EVAL_DIR):
    if not fname.endswith(".json"):
        continue
    config = parse_config(fname)
    if not config:
        continue
    with open(os.path.join(EVAL_DIR, fname)) as f:
        data = json.load(f)
        for entry in data:
            if all(m in entry for m in ["bleu", "rouge-l", "bertscore", "f1_score"]):
                records.append({
                    "top_k": config[0],
                    "top_p": config[1],
                    "chunking": config[2],
                    "bleu": entry["bleu"],
                    "rouge-l": entry["rouge-l"],
                    "bertscore": entry["bertscore"],
                    "f1_score": entry["f1_score"]
                })

df = pd.DataFrame(records)

# Compute mean scores per config
means = df.groupby(["top_k", "top_p", "chunking"]).mean().reset_index()

# Find best configs per metric
for metric in ["bleu", "rouge-l", "bertscore", "f1_score"]:
    best = means.sort_values(metric, ascending=False).head(1)
    row = best.iloc[0]
    print(f"🔍 Best config for {metric.upper()}: top_k={row['top_k']}, top_p={row['top_p']}, chunking={row['chunking']} — Score: {row[metric]:.4f}")
