import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# File paths for embedding model evaluation results
emb_model_1_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/emb_model/evaluation/evaluation_results_50_0.55_1000_200.json"
emb_model_2_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/emb_model/evaluation/evaluation_results_mpnet_after_grid.json"
output_dir = "/home/ariadnipap/thesis_chatbot_project/data/eval/emb_model/stats_after_grid/"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load JSON files
with open(emb_model_1_path, "r", encoding="utf-8") as f:
    data_model_1 = json.load(f)

with open(emb_model_2_path, "r", encoding="utf-8") as f:
    data_model_2 = json.load(f)

# Convert to DataFrame
df_model_1 = pd.DataFrame(data_model_1)
df_model_2 = pd.DataFrame(data_model_2)

# Add embedding model column
df_model_1["embedding_model"] = "MiniLM"
df_model_2["embedding_model"] = "MPNet"

# Combine datasets
df = pd.concat([df_model_1, df_model_2])

# Select numeric columns for comparison
metrics = [
    "faithfulness_score", "answer_relevance_score", "context_relevance_score",
    "groundedness_score", "bleu", "rouge-l", "bertscore",
    "precision@k", "f1_score"
]

# Compute summary statistics and save as CSV
summary_stats = df.groupby("embedding_model")[metrics].agg(["mean", "std", "min", "max"])
summary_stats.to_csv(os.path.join(output_dir, "summary_statistics.csv"))

# ✅ Bar Plot: Mean Score Comparison
plt.figure(figsize=(12, 7))
mean_scores = df.groupby("embedding_model")[metrics].mean().T
mean_scores.plot(kind="bar", figsize=(12, 7), colormap="coolwarm", edgecolor="black")
plt.title("Comparison of Average Performance Metrics (Embedding Models)", fontsize=14)
plt.ylabel("Average Score", fontsize=12)
plt.xticks(rotation=45, fontsize=11)
plt.legend(title="Embedding Model", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "barplot_mean_scores.png"))
plt.close()

# ✅ Metric Distribution: Discrete Count vs Histogram
for metric in metrics:
    plt.figure(figsize=(8, 5))

    # Check if the metric is discrete (Likert scale)
    is_discrete = (
        df[metric].dropna().apply(lambda x: isinstance(x, (int, float)) and float(x).is_integer()).all()
        and df[metric].nunique() <= 6
    )

    if is_discrete:
        sns.countplot(data=df, x=metric, hue="embedding_model", palette=["blue", "red"], edgecolor="black")
        plt.title(f"Distribution of {metric} (Count)", fontsize=13)
        plt.ylabel("Count", fontsize=12)
    else:
        sns.histplot(data=df, x=metric, hue="embedding_model", bins=10, multiple="dodge",
                     palette=["blue", "red"], edgecolor="black", kde=False)
        plt.title(f"Histogram of {metric}", fontsize=13)
        plt.ylabel("Frequency", fontsize=12)

    plt.xlabel(metric, fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"distribution_{metric}.png"))
    plt.close()

# ✅ Scatter Plots: Side-by-side per metric
fig, axes = plt.subplots(3, 3, figsize=(14, 12))
axes = axes.flatten()

for i, metric in enumerate(metrics):
    sns.scatterplot(
        x=df_model_1[metric],
        y=df_model_2[metric],
        ax=axes[i],
        color="purple",
        alpha=0.7
    )
    axes[i].set_title(f"{metric}: MiniLM vs. MPNet", fontsize=12)
    axes[i].set_xlabel("MiniLM", fontsize=11)
    axes[i].set_ylabel("MPNet", fontsize=11)
    axes[i].grid(linestyle="--", alpha=0.6)

    # Add y=x line
    min_val = min(df_model_1[metric].min(), df_model_2[metric].min())
    max_val = max(df_model_1[metric].max(), df_model_2[metric].max())
    axes[i].plot([min_val, max_val], [min_val, max_val], "r--", lw=1)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "scatterplots_embedding_model_comparison.png"))
plt.close()

print(f"✅ Comparison of embedding models completed. Results saved in: {output_dir}")
