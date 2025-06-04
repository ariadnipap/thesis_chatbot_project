import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

# Paths and setup
EVAL_DIR = "/home/ariadnipap/thesis_chatbot_project/evaluation/evaluation_approach_1/evaluation_with_preprocessing"
OUTPUT_DIR = "/home/ariadnipap/thesis_chatbot_project/evaluation/evaluation_approach_1/normalized-plots-results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

top_k_values = [10, 25, 50]
top_p_values = [0.55, 0.7, 0.88]
chunking_modes = ["no_chunking", "1000_100", "2000_200"]

# Parse config
def parse_filename(filename):
    pattern = r"evaluation_results_(\d+)_([0-9.]+)_(no_chunking|1000_100|2000_200)\.json"
    match = re.match(pattern, filename)
    if match:
        return int(match.group(1)), float(match.group(2)), match.group(3)
    return None

# Normalize function
def normalize_1_to_5(score):
    return (score - 1) / 4 * 100

# Compute normalized optimization score (faithfulness removed)
def compute_optimization_score(entry):
    keys = ["groundedness_score", "answer_relevance_score", "context_relevance_score"]
    if all(k in entry and isinstance(entry[k], (int, float)) for k in keys):
        ground = normalize_1_to_5(entry["groundedness_score"])
        rel = normalize_1_to_5((entry["answer_relevance_score"] + entry["context_relevance_score"]) / 2)
        return 0.5 * rel + 0.5 * ground
    return None

# Load and compute scores
score_map = {}
all_scores = []

for fname in os.listdir(EVAL_DIR):
    if not fname.endswith(".json"):
        continue
    config = parse_filename(fname)
    if not config:
        continue
    with open(os.path.join(EVAL_DIR, fname), "r") as f:
        data = json.load(f)
        scores = [compute_optimization_score(entry) for entry in data if compute_optimization_score(entry) is not None]
        if not scores:
            print(f"⚠️ No valid entries in {fname}")
            continue
        mean_score = round(np.mean(scores), 4)
        score_map[config] = mean_score
        for s in scores:
            all_scores.append((config, s))

# Generate heatmap and 3D surface for each chunking mode
for chunking in chunking_modes:
    heatmap_data = np.zeros((len(top_p_values), len(top_k_values)))

    for i, top_p in enumerate(top_p_values):
        for j, top_k in enumerate(top_k_values):
            score = score_map.get((top_k, top_p, chunking), np.nan)
            heatmap_data[i, j] = round(score, 4) if score else np.nan

    # --- Heatmap ---
    plt.figure(figsize=(8, 6))
    sns.heatmap(heatmap_data, annot=True, xticklabels=top_k_values, yticklabels=top_p_values, cmap="YlGnBu", linewidths=0.5)
    plt.title(f"Heatmap of Normalized Scores (0–100) — {chunking}")
    plt.xlabel("Top-K")
    plt.ylabel("Top-P")
    plt.tight_layout()
    heatmap_path = os.path.join(OUTPUT_DIR, f"heatmap_{chunking}.png")
    plt.savefig(heatmap_path)
    plt.close()
    print(f"✅ Saved heatmap: {heatmap_path}")

    # --- 3D Surface ---
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    X, Y = np.meshgrid(top_k_values, top_p_values)
    Z = heatmap_data

    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, edgecolor='k')
    ax.set_title(f"3D Surface (Normalized Score) — {chunking}")
    ax.set_xlabel("Top-K")
    ax.set_ylabel("Top-P")
    ax.set_zlabel("Score (0–100)")
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
    plt.tight_layout()
    surface_path = os.path.join(OUTPUT_DIR, f"surface_{chunking}.png")
    plt.savefig(surface_path)
    plt.close()
    print(f"✅ Saved surface: {surface_path}")
