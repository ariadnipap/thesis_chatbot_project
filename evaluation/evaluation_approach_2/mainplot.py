import os
import json
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import defaultdict

# === CONFIGURATION ===
EVAL_DIR = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/evaluation_with_preprocessing/"
top_k_values = [10, 25, 50]
top_p_values = [0.55, 0.7, 0.88]
chunking_modes = ["no_chunking", "chunked_1000_100", "chunked_2000_200"]

# === Parse config from filename ===
def parse_config(filename):
    if "no_chunking" in filename:
        match = re.match(r"evaluation_results_(\d+)_([0-9.]+)_no_chunking\.json", filename)
        if match:
            return int(match.group(1)), float(match.group(2)), "no_chunking"
    else:
        match = re.match(r"evaluation_results_(\d+)_([0-9.]+)_chunked_(\d+)_(\d+)\.json", filename)
        if match:
            chunking = f"chunked_{match.group(3)}_{match.group(4)}"
            return int(match.group(1)), float(match.group(2)), chunking
    return None

# === Normalization function ===
def normalize_1_to_5(score):
    return (score - 1) / 4 * 100

# === Load scores into DataFrame ===
data = []
for fname in os.listdir(EVAL_DIR):
    if not fname.endswith(".json"):
        continue
    config = parse_config(fname)
    if not config:
        continue
    top_k, top_p, chunking = config
    with open(os.path.join(EVAL_DIR, fname), "r") as f:
        entries = json.load(f)
        scores = [
            normalize_1_to_5(entry["evaluation_score"])
            for entry in entries
            if isinstance(entry.get("evaluation_score"), (int, float))
        ]
        if scores:
            mean_score = round(float(np.mean(scores)), 4)
            label = f"({top_k}, {top_p})"
            data.append({
                "top_k": top_k,
                "top_p": top_p,
                "chunking": chunking,
                "label": label,
                "score": mean_score
            })

df = pd.DataFrame(data)

# === Sort by (top_k, top_p) for clean x-axis ===
df["label"] = pd.Categorical(
    df["label"],
    categories=sorted(
        df["label"].unique(),
        key=lambda x: (int(x.split(",")[0][1:]), float(x.split(",")[1][:-1]))
    ),
    ordered=True
)

# === Plot grouped barplot ===
plt.figure(figsize=(14, 6))
sns.barplot(data=df, x="label", y="score", hue="chunking", palette="Set2")

plt.title("Normalized Evaluation Scores for All Parameter Combinations")
plt.xlabel("Configuration (Top-K, Top-P)")
plt.ylabel("Mean Score (0–100)")
plt.ylim(0, 100)
plt.xticks(rotation=45)
plt.legend(title="Chunking Strategy")
plt.tight_layout()
plt.savefig("barplot_all_27_configs_normalized.png")
plt.close()

print("✅ Saved normalized barplot: barplot_all_27_configs_normalized.png")
