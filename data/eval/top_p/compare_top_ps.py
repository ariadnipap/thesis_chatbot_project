import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# File paths for top_p evaluation results
top_p_088_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_p/evaluation/evaluation_results_60.json"
top_p_07_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_p/evaluation/evaluation_results_top_p_0.7.json"
top_p_055_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_p/evaluation/evaluation_results_top_p_0.55.json"
output_dir = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_p/stats/"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load JSON files
with open(top_p_088_path, "r", encoding="utf-8") as f:
    data_088 = json.load(f)

with open(top_p_07_path, "r", encoding="utf-8") as f:
    data_07 = json.load(f)

with open(top_p_055_path, "r", encoding="utf-8") as f:
    data_055 = json.load(f)

# Convert to DataFrame
df_088 = pd.DataFrame(data_088)
df_07 = pd.DataFrame(data_07)
df_055 = pd.DataFrame(data_055)

# Add top_p column
df_088["top_p"] = 0.88
df_07["top_p"] = 0.7
df_055["top_p"] = 0.55

# Combine datasets
df = pd.concat([df_088, df_07, df_055])

# Select numeric columns for comparison
metrics = [
    "faithfulness_score", "answer_relevance_score", "context_relevance_score",
    "groundedness_score", "bleu", "rouge-l", "bertscore",
    "precision@k", "f1_score"
]

# Compute summary statistics and save as CSV
summary_stats = df.groupby("top_p")[metrics].agg(["mean", "std", "min", "max"])
summary_stats.to_csv(os.path.join(output_dir, "summary_statistics.csv"))

# **Bar Plot: Mean Score Comparison**
plt.figure(figsize=(12, 7))
mean_scores = df.groupby("top_p")[metrics].mean().T
mean_scores.plot(kind="bar", figsize=(12, 7), colormap="coolwarm", edgecolor="black")
plt.title("Comparison of Average Performance Metrics at Different Top-P Values", fontsize=14)
plt.ylabel("Average Score", fontsize=12)
plt.xticks(rotation=45, fontsize=11)
plt.legend(title="Top-P", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "barplot_mean_scores.png"))
plt.close()

# **Density Plots: Score Distribution**
for metric in metrics:
    plt.figure(figsize=(8, 5))
    sns.kdeplot(df[df["top_p"] == 0.88][metric], label="Top-P = 0.88", fill=True, color="blue", alpha=0.5)
    sns.kdeplot(df[df["top_p"] == 0.7][metric], label="Top-P = 0.7", fill=True, color="red", alpha=0.5)
    sns.kdeplot(df[df["top_p"] == 0.55][metric], label="Top-P = 0.55", fill=True, color="green", alpha=0.5)
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
    sns.scatterplot(x=df_088[metric], y=df_07[metric], ax=axes[i], color="purple", alpha=0.7, label="0.88 vs. 0.7")
    sns.scatterplot(x=df_088[metric], y=df_055[metric], ax=axes[i], color="orange", alpha=0.7, label="0.88 vs. 0.55")
    sns.scatterplot(x=df_07[metric], y=df_055[metric], ax=axes[i], color="green", alpha=0.7, label="0.7 vs. 0.55")
    
    axes[i].set_title(f"{metric}: Top-P Comparisons", fontsize=12)
    axes[i].set_xlabel("Higher Top-P Value", fontsize=11)
    axes[i].set_ylabel("Lower Top-P Value", fontsize=11)
    axes[i].grid(linestyle="--", alpha=0.6)
    axes[i].legend()

    # **Fixed: Get the min/max values correctly**
    min_val = min(df_088[metric].min(), df_07[metric].min(), df_055[metric].min())
    max_val = max(df_088[metric].max(), df_07[metric].max(), df_055[metric].max())
    axes[i].plot([min_val, max_val], [min_val, max_val], "r--", lw=1)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "scatterplots_top_p_comparison.png"))
plt.close()

print(f"✅ Comparison of top_p values completed. Results saved in: {output_dir}")
