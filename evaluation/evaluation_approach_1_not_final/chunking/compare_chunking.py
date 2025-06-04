import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

#text splitting

# File paths for chunking evaluation results
non_chunking_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/chunking/evaluation/evaluation_results_60.json"
chunking_500_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/chunking/evaluation/evaluation_results_chunked.json"
output_dir = "/home/ariadnipap/thesis_chatbot_project/data/eval/chunking/stats/"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load JSON files
with open(non_chunking_path, "r", encoding="utf-8") as f:
    data_non_chunking = json.load(f)

with open(chunking_500_path, "r", encoding="utf-8") as f:
    data_chunking_500 = json.load(f)

# Convert to DataFrame
df_non_chunking = pd.DataFrame(data_non_chunking)
df_chunking_500 = pd.DataFrame(data_chunking_500)

# Add chunking method column
df_non_chunking["chunking"] = "No Chunking"
df_chunking_500["chunking"] = "Chunking (500)"

# Combine datasets
df = pd.concat([df_non_chunking, df_chunking_500])

# Select numeric columns for comparison
metrics = [
    "faithfulness_score", "answer_relevance_score", "context_relevance_score",
    "groundedness_score", "bleu", "rouge-l", "bertscore",
    "precision@k", "f1_score"
]

# Compute summary statistics and save as CSV
summary_stats = df.groupby("chunking")[metrics].agg(["mean", "std", "min", "max"])
summary_stats.to_csv(os.path.join(output_dir, "summary_statistics.csv"))

# **Bar Plot: Mean Score Comparison**
plt.figure(figsize=(12, 7))
mean_scores = df.groupby("chunking")[metrics].mean().T
mean_scores.plot(kind="bar", figsize=(12, 7), colormap="coolwarm", edgecolor="black")
plt.title("Comparison of Average Performance Metrics (Chunking vs. Non-Chunking)", fontsize=14)
plt.ylabel("Average Score", fontsize=12)
plt.xticks(rotation=45, fontsize=11)
plt.legend(title="Chunking Method", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "barplot_mean_scores.png"))
plt.close()

# **Density Plots: Score Distribution**
for metric in metrics:
    plt.figure(figsize=(8, 5))
    sns.kdeplot(df[df["chunking"] == "No Chunking"][metric], label="No Chunking", shade=True, color="blue", alpha=0.5)
    sns.kdeplot(df[df["chunking"] == "Chunking (500)"][metric], label="Chunking (500)", shade=True, color="red", alpha=0.5)
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
    sns.scatterplot(x=df_non_chunking[metric], y=df_chunking_500[metric], ax=axes[i], color="purple", alpha=0.7)
    axes[i].set_title(f"{metric}: Non-Chunking vs. Chunking (500)", fontsize=12)
    axes[i].set_xlabel("No Chunking", fontsize=11)
    axes[i].set_ylabel("Chunking (500)", fontsize=11)
    axes[i].grid(linestyle="--", alpha=0.6)

    # **Add diagonal reference line (y=x)**
    min_val = min(df_non_chunking[metric].min(), df_chunking_500[metric].min())
    max_val = max(df_non_chunking[metric].max(), df_chunking_500[metric].max())
    axes[i].plot([min_val, max_val], [min_val, max_val], "r--", lw=1)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "scatterplots_chunking_comparison.png"))
plt.close()

print(f"✅ Comparison of chunking methods completed. Results saved in: {output_dir}")
