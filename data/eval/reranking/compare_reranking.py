import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# File paths for reranking evaluation results
non_reranking_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/reranking/evaluation/evaluation_results_no_reranking.json"
reranking_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/reranking/evaluation/evaluation_results_60.json"
output_dir = "/home/ariadnipap/thesis_chatbot_project/data/eval/reranking/stats/"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load JSON files
with open(non_reranking_path, "r", encoding="utf-8") as f:
    data_non_reranking = json.load(f)

with open(reranking_path, "r", encoding="utf-8") as f:
    data_reranking = json.load(f)

# Convert to DataFrame
df_non_reranking = pd.DataFrame(data_non_reranking)
df_reranking = pd.DataFrame(data_reranking)

# Add reranking method column
df_non_reranking["reranking"] = "No Reranking"
df_reranking["reranking"] = "With Reranking"

# Combine datasets
df = pd.concat([df_non_reranking, df_reranking])

# Select numeric columns for comparison
metrics = [
    "faithfulness_score", "answer_relevance_score", "context_relevance_score",
    "groundedness_score", "bleu", "rouge-l", "bertscore",
    "precision@k", "f1_score"
]

# Compute summary statistics and save as CSV
summary_stats = df.groupby("reranking")[metrics].agg(["mean", "std", "min", "max"])
summary_stats.to_csv(os.path.join(output_dir, "summary_statistics.csv"))

# **Bar Plot: Mean Score Comparison**
plt.figure(figsize=(12, 7))
mean_scores = df.groupby("reranking")[metrics].mean().T
mean_scores.plot(kind="bar", figsize=(12, 7), colormap="coolwarm", edgecolor="black")
plt.title("Comparison of Average Performance Metrics (Reranking vs. No Reranking)", fontsize=14)
plt.ylabel("Average Score", fontsize=12)
plt.xticks(rotation=45, fontsize=11)
plt.legend(title="Reranking Method", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "barplot_mean_scores.png"))
plt.close()

# **Density Plots: Score Distribution**
for metric in metrics:
    plt.figure(figsize=(8, 5))
    sns.kdeplot(df[df["reranking"] == "No Reranking"][metric], label="No Reranking", shade=True, color="blue", alpha=0.5)
    sns.kdeplot(df[df["reranking"] == "With Reranking"][metric], label="With Reranking", shade=True, color="red", alpha=0.5)
    plt.title(f"Density Distribution of {metric}", fontsize=13)
    plt.xlabel(metric, fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(linestyle="--", alpha=0.6)
    plt.savefig(os.path.join(output_dir, f"density_{metric}.png"))
    plt.close()

# **Scatter Plots: Direct Comparisons**
fig, axes = plt.subplots(3, 3, figsize=(14, 12))
axes = axes.flatten()

for i, metric in enumerate(metrics):
    sns.scatterplot(x=df_non_reranking[metric], y=df_reranking[metric], ax=axes[i], color="purple", alpha=0.7)
    axes[i].set_title(f"{metric}: No Reranking vs. With Reranking", fontsize=12)
    axes[i].set_xlabel("No Reranking", fontsize=11)
    axes[i].set_ylabel("With Reranking", fontsize=11)
    axes[i].grid(linestyle="--", alpha=0.6)

    # **Add diagonal reference line (y=x)**
    min_val = min(df_non_reranking[metric].min(), df_reranking[metric].min())
    max_val = max(df_non_reranking[metric].max(), df_reranking[metric].max())
    axes[i].plot([min_val, max_val], [min_val, max_val], "r--", lw=1)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "scatterplots_reranking_comparison.png"))
plt.close()

print(f"✅ Comparison of reranking methods completed. Results saved in: {output_dir}")
