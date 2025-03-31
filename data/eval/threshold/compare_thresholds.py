import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# File paths
threshold_8_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/threshold/evaluation/evaluation_results_60.json"
threshold_3_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/threshold/evaluation/evaluation_results_threshold_-3.0_60.json"
output_dir = "/home/ariadnipap/thesis_chatbot_project/data/eval/threshold/stats/"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load JSON files
with open(threshold_8_path, "r", encoding="utf-8") as f:
    data_8 = json.load(f)

with open(threshold_3_path, "r", encoding="utf-8") as f:
    data_3 = json.load(f)

# Convert to DataFrame
df_8 = pd.DataFrame(data_8)
df_3 = pd.DataFrame(data_3)

# Add threshold column
df_8["threshold"] = -8
df_3["threshold"] = -3

# Combine datasets
df = pd.concat([df_8, df_3])

# Select numeric columns
metrics = [
    "faithfulness_score", "answer_relevance_score", "context_relevance_score",
    "groundedness_score", "bleu", "rouge-l", "bertscore",
    "precision@k", "f1_score"
]

# Compute summary statistics and save as CSV
summary_stats = df.groupby("threshold")[metrics].agg(["mean", "std", "min", "max"])
summary_stats.to_csv(os.path.join(output_dir, "summary_statistics.csv"))

# **Bar Plot: Mean Score Comparison**
plt.figure(figsize=(12, 7))
mean_scores = df.groupby("threshold")[metrics].mean().T
mean_scores.plot(kind="bar", figsize=(12, 7), colormap="coolwarm", edgecolor="black")
plt.title("Comparison of Average Performance Metrics at Different Thresholds", fontsize=14)
plt.ylabel("Average Score", fontsize=12)
plt.xticks(rotation=45, fontsize=11)
plt.legend(title="Threshold", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "barplot_mean_scores.png"))
plt.close()

# **Density Plots: Score Distribution**
for metric in metrics:
    plt.figure(figsize=(8, 5))
    sns.kdeplot(df[df["threshold"] == -8][metric], label="Threshold -8", shade=True, color="blue", alpha=0.5)
    sns.kdeplot(df[df["threshold"] == -3][metric], label="Threshold -3", shade=True, color="red", alpha=0.5)
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
    sns.scatterplot(x=df_8[metric], y=df_3[metric], ax=axes[i], color="purple", alpha=0.7)
    axes[i].set_title(f"{metric}: Threshold -8 vs. -3", fontsize=12)
    axes[i].set_xlabel("Threshold -8", fontsize=11)
    axes[i].set_ylabel("Threshold -3", fontsize=11)
    axes[i].grid(linestyle="--", alpha=0.6)
    
    # **Add diagonal reference line (y=x)**
    min_val = min(df_8[metric].min(), df_3[metric].min())
    max_val = max(df_8[metric].max(), df_3[metric].max())
    axes[i].plot([min_val, max_val], [min_val, max_val], "r--", lw=1)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "scatterplots_threshold_comparison.png"))
plt.close()

print(f"✅ Improved plots and summary statistics saved in: {output_dir}")
