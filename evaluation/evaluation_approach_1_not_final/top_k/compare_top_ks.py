import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# File paths for top_k evaluation results
top_k_50_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_k/evaluation/evaluation_results_60.json"
top_k_25_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_k/evaluation/evaluation_results_top_k_25.json"
top_k_10_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_k/evaluation/evaluation_results_top_k_10.json"
output_dir = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_k/stats/"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load JSON files
with open(top_k_50_path, "r", encoding="utf-8") as f:
    data_50 = json.load(f)

with open(top_k_25_path, "r", encoding="utf-8") as f:
    data_25 = json.load(f)

with open(top_k_10_path, "r", encoding="utf-8") as f:
    data_10 = json.load(f)

# Convert to DataFrame
df_50 = pd.DataFrame(data_50)
df_25 = pd.DataFrame(data_25)
df_10 = pd.DataFrame(data_10)

# Add top_k column
df_50["top_k"] = 50
df_25["top_k"] = 25
df_10["top_k"] = 10

# Combine datasets
df = pd.concat([df_50, df_25, df_10])

# Select numeric columns for comparison
metrics = [
    "faithfulness_score", "answer_relevance_score", "context_relevance_score",
    "groundedness_score", "bleu", "rouge-l", "bertscore",
    "precision@k", "f1_score"
]

# Compute summary statistics and save as CSV
summary_stats = df.groupby("top_k")[metrics].agg(["mean", "std", "min", "max"])
summary_stats.to_csv(os.path.join(output_dir, "summary_statistics.csv"))

# **Bar Plot: Mean Score Comparison**
plt.figure(figsize=(12, 7))
mean_scores = df.groupby("top_k")[metrics].mean().T
mean_scores.plot(kind="bar", figsize=(12, 7), colormap="coolwarm", edgecolor="black")
plt.title("Comparison of Average Performance Metrics at Different Top-K Values", fontsize=14)
plt.ylabel("Average Score", fontsize=12)
plt.xticks(rotation=45, fontsize=11)
plt.legend(title="Top-K", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "barplot_mean_scores.png"))
plt.close()

# **Density Plots: Score Distribution**
for metric in metrics:
    plt.figure(figsize=(8, 5))
    sns.kdeplot(df[df["top_k"] == 50][metric], label="Top-K = 50", shade=True, color="blue", alpha=0.5)
    sns.kdeplot(df[df["top_k"] == 25][metric], label="Top-K = 25", shade=True, color="red", alpha=0.5)
    sns.kdeplot(df[df["top_k"] == 10][metric], label="Top-K = 10", shade=True, color="green", alpha=0.5)
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
    sns.scatterplot(x=df_50[metric], y=df_25[metric], ax=axes[i], color="purple", alpha=0.7, label="50 vs. 25")
    sns.scatterplot(x=df_50[metric], y=df_10[metric], ax=axes[i], color="orange", alpha=0.7, label="50 vs. 10")
    sns.scatterplot(x=df_25[metric], y=df_10[metric], ax=axes[i], color="green", alpha=0.7, label="25 vs. 10")
    
    axes[i].set_title(f"{metric}: Top-K Comparisons", fontsize=12)
    axes[i].set_xlabel("Higher Top-K Value", fontsize=11)
    axes[i].set_ylabel("Lower Top-K Value", fontsize=11)
    axes[i].grid(linestyle="--", alpha=0.6)
    axes[i].legend()

    # **Add diagonal reference line (y=x)**
    min_val = min(df[metric].min())
    max_val = max(df[metric].max())
    axes[i].plot([min_val, max_val], [min_val, max_val], "r--", lw=1)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "scatterplots_top_k_comparison.png"))
plt.close()

print(f"✅ Comparison of top_k values completed. Results saved in: {output_dir}")
