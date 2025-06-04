import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re

# Config
EVAL_DIR = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/evaluation_with_preprocessing/"
OUTPUT_PATH = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/traditional_metrics_grid.png"

top_k_values = [10, 25, 50]
top_p_values = [0.55, 0.7, 0.88]
chunking_modes = ["chunked_1000_100", "chunked_2000_200", "no_chunking"]

# Filename parser
def parse_config(filename):
    match = re.match(r"evaluation_results_(\d+)_([0-9.]+)_(chunked_\d+_\d+|no_chunking)\.json", filename)
    if match:
        top_k = int(match.group(1))
        top_p = float(match.group(2))
        chunking = match.group(3)
        return top_k, top_p, chunking
    return None

# Collect scores
records = []

for fname in os.listdir(EVAL_DIR):
    if not fname.endswith(".json"):
        continue
    config = parse_config(fname)
    if not config:
        continue
    filepath = os.path.join(EVAL_DIR, fname)
    with open(filepath, "r") as f:
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

# Create DataFrame
df = pd.DataFrame(records)

# Group by config and compute means
summary_df = df.groupby(["top_k", "top_p", "chunking"]).mean().reset_index()

# Melt for seaborn plotting
melted_df = summary_df.melt(
    id_vars=["top_k", "top_p", "chunking"],
    value_vars=["bleu", "rouge-l", "bertscore", "f1_score"],
    var_name="metric", value_name="score"
)

# Plot
sns.set(style="whitegrid")
g = sns.catplot(
    data=melted_df,
    x="metric", y="score", hue="chunking", col="top_k", row="top_p",
    kind="bar", height=3.5, aspect=1.2
)

g.fig.subplots_adjust(top=0.92)
g.fig.suptitle("Traditional Metrics Across Configurations", fontsize=16)
g.savefig(OUTPUT_PATH)
plt.show()
