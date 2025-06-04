import os
import json
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import defaultdict
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

# Configuration
EVAL_DIR = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/evaluation_with_preprocessing/"

top_k_values = [10, 25, 50]
top_p_values = [0.55, 0.7, 0.88]
chunking_modes = ["no_chunking", "chunked_1000_100", "chunked_2000_200"]

# Normalize function: 1–5 → 0–100
def normalize_1_to_5(score):
    return (score - 1) / 4 * 100

# Parse filename into config tuple
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

# Load and normalize all scores
score_map = {}
all_scores = []

for fname in os.listdir(EVAL_DIR):
    if not fname.endswith(".json"):
        continue
    config = parse_config(fname)
    if not config:
        continue
    with open(os.path.join(EVAL_DIR, fname), "r") as f:
        data = json.load(f)
        scores = [normalize_1_to_5(entry.get("evaluation_score")) for entry in data if isinstance(entry.get("evaluation_score"), (int, float))]
        if scores:
            mean_score = round(float(np.mean(scores)), 4)
            score_map[config] = mean_score
            for s in scores:
                all_scores.append((config, s))

# ========== 1. Heatmap + 3D surface per chunking strategy ==========
for chunking in chunking_modes:
    matrix = np.zeros((len(top_p_values), len(top_k_values)))

    for i, top_p in enumerate(top_p_values):
        for j, top_k in enumerate(top_k_values):
            matrix[i, j] = score_map.get((top_k, top_p, chunking), np.nan)

    # Heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, xticklabels=top_k_values, yticklabels=top_p_values, cmap="YlGnBu", linewidths=0.5)
    plt.title(f"Heatmap of Normalized Evaluation Scores - {chunking}")
    plt.xlabel("Top-K")
    plt.ylabel("Top-P")
    plt.tight_layout()
    plt.savefig(f"heatmap_normalized_{chunking}.png")
    plt.close()

    # 3D Surface
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    X, Y = np.meshgrid(top_k_values, top_p_values)
    Z = matrix

    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, edgecolor='k')
    ax.set_title(f"3D Surface (Normalized) - {chunking}")
    ax.set_xlabel("Top-K")
    ax.set_ylabel("Top-P")
    ax.set_zlabel("Mean Score (0–100)")
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
    plt.tight_layout()
    plt.savefig(f"surface_normalized_{chunking}.png")
    plt.close()

# ========== 2. Comparison of Chunking Strategies ==========
chunking_scores = defaultdict(list)
for (top_k, top_p, chunking), score in all_scores:
    chunking_scores[chunking].append(score)

chunking_df = pd.DataFrame([
    {"chunking": chunk, "score": score}
    for chunk, scores in chunking_scores.items()
    for score in scores
])

# Mean score barplot
mean_scores = chunking_df.groupby("chunking")["score"].mean().reset_index()

plt.figure(figsize=(7, 5))
sns.barplot(data=mean_scores, x="chunking", y="score", palette="deep")
plt.title("Normalized Mean Evaluation Score per Chunking Strategy")
plt.xlabel("Chunking Strategy")
plt.ylabel("Mean Score (0–100)")
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig("barplot_chunking_means_normalized.png")
plt.close()

print("✅ All normalized plots saved.")
