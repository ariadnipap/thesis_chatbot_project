import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import defaultdict

# Paths
EVAL_DIR = "/home/ariadnipap/thesis_chatbot_project/evaluation/evaluation_approach_1/evaluation_with_preprocessing"
OUTPUT_PATH = "/home/ariadnipap/thesis_chatbot_project/evaluation/evaluation_approach_1/normalized-plots-results/barplot_chunking_means_normalized.png"

# Normalization function
def normalize_1_to_5(score):
    return (score - 1) / 4 * 100

# Scoring function (faithfulness removed)
def compute_optimization_score(entry):
    keys = ["groundedness_score", "answer_relevance_score", "context_relevance_score"]
    if all(k in entry for k in keys):
        ground = normalize_1_to_5(entry["groundedness_score"])
        rel = normalize_1_to_5((entry["answer_relevance_score"] + entry["context_relevance_score"]) / 2)
        return 0.5 * rel + 0.5 * ground
    return None

# Group scores per chunking strategy
chunking_scores = defaultdict(list)

pattern = r"evaluation_results_(\d+)_([0-9.]+)_(no_chunking|1000_100|2000_200)\.json"

for fname in os.listdir(EVAL_DIR):
    match = re.match(pattern, fname)
    if not match:
        continue
    chunking = match.group(3)
    with open(os.path.join(EVAL_DIR, fname), "r") as f:
        data = json.load(f)
        for entry in data:
            score = compute_optimization_score(entry)
            if score is not None:
                chunking_scores[chunking].append(score)

# Convert to DataFrame for plotting
plot_df = pd.DataFrame({
    "chunking": list(chunking_scores.keys()),
    "mean_score": [np.mean(scores) for scores in chunking_scores.values()]
})

# Plot
plt.figure(figsize=(6, 5))
sns.barplot(data=plot_df, x="chunking", y="mean_score", palette="colorblind")
plt.title("Normalized Mean Evaluation Score Per Chunking Strategy")
plt.xlabel("Chunking Strategy")
plt.ylabel("Mean Score (0–100)")
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig(OUTPUT_PATH)
plt.close()

print(f"✅ Saved normalized chunking plot: {OUTPUT_PATH}")
