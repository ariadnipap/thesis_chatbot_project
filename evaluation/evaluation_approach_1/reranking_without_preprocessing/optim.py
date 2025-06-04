import json
import os
import pandas as pd

# File paths
reranking_path = "/home/ariadnipap/thesis_chatbot_project/data/eval_after_filter/reranking/evaluation/evaluation_results_10_0.7_1000_200_new.json"
non_reranking_path = "/home/ariadnipap/thesis_chatbot_project/data/eval_after_filter/reranking/evaluation/evaluation_results_10_0.7_1000_200_no_reranking.json"
output_file = "/home/ariadnipap/thesis_chatbot_project/data/eval_after_filter/reranking/stats/optimization_comparison_reranking.json"

# Load JSON files
with open(reranking_path, "r", encoding="utf-8") as f:
    data_reranking = json.load(f)

with open(non_reranking_path, "r", encoding="utf-8") as f:
    data_non_reranking = json.load(f)

# Convert to DataFrame
df_reranking = pd.DataFrame(data_reranking)
df_non_reranking = pd.DataFrame(data_non_reranking)

# Compute Relevance (average of answer and context relevance)
df_reranking["relevance"] = (df_reranking["answer_relevance_score"] + df_reranking["context_relevance_score"]) / 2
df_non_reranking["relevance"] = (df_non_reranking["answer_relevance_score"] + df_non_reranking["context_relevance_score"]) / 2

# Compute Optimization Score
def compute_optimization_score(df):
    return (
        0.5 * df["faithfulness_score"] +
        0.25 * df["relevance"] +
        0.25 * df["groundedness_score"]
    )

df_reranking["optimization_score"] = compute_optimization_score(df_reranking)
df_non_reranking["optimization_score"] = compute_optimization_score(df_non_reranking)

# Compute Mean Optimization Score for Each Setting
mean_opt_score_reranking = df_reranking["optimization_score"].mean()
mean_opt_score_non_reranking = df_non_reranking["optimization_score"].mean()

# Store results
best_reranking_setting = "With Reranking" if mean_opt_score_reranking > mean_opt_score_non_reranking else "No Reranking"

results = {
    "reranking": mean_opt_score_reranking,
    "no_reranking": mean_opt_score_non_reranking,
    "better_setting": best_reranking_setting
}

# Save results to JSON
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

# Print the best setting
print(f"✅ Optimization comparison completed. Results saved in: {output_file}")
print(f"🔍 Mean Optimization Score With Reranking: {mean_opt_score_reranking:.4f}")
print(f"🔍 Mean Optimization Score Without Reranking: {mean_opt_score_non_reranking:.4f}")
print(f"🏆 Best Setting to Proceed With: {results['better_setting']}")
