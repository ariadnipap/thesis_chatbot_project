import json
import os
import pandas as pd

# File paths
top_k_50_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_k/evaluation/evaluation_results_60.json"
top_k_25_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_k/evaluation/evaluation_results_top_k_25.json"
top_k_10_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_k/evaluation/evaluation_results_top_k_10.json"
output_file = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_k/stats/optimization_comparison.json"

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

# Compute Relevance (average of answer and context relevance)
df_50["relevance"] = (df_50["answer_relevance_score"] + df_50["context_relevance_score"]) / 2
df_25["relevance"] = (df_25["answer_relevance_score"] + df_25["context_relevance_score"]) / 2
df_10["relevance"] = (df_10["answer_relevance_score"] + df_10["context_relevance_score"]) / 2

# Compute Optimization Score
def compute_optimization_score(df):
    return (
        0.5 * df["faithfulness_score"] +
        0.25 * df["relevance"] +
        0.25 * df["groundedness_score"]
    )

df_50["optimization_score"] = compute_optimization_score(df_50)
df_25["optimization_score"] = compute_optimization_score(df_25)
df_10["optimization_score"] = compute_optimization_score(df_10)

# Compute Mean Optimization Score for Each Top-K Value
mean_opt_score_50 = df_50["optimization_score"].mean()
mean_opt_score_25 = df_25["optimization_score"].mean()
mean_opt_score_10 = df_10["optimization_score"].mean()

# Store results
best_top_k = max([(50, mean_opt_score_50), (25, mean_opt_score_25), (10, mean_opt_score_10)], key=lambda x: x[1])[0]

results = {
    "top_k_50": mean_opt_score_50,
    "top_k_25": mean_opt_score_25,
    "top_k_10": mean_opt_score_10,
    "better_top_k": best_top_k
}

# Save results to JSON
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

# Print the best top_k value
print(f"✅ Optimization comparison completed. Results saved in: {output_file}")
print(f"🔍 Mean Optimization Score at Top-K 50: {mean_opt_score_50:.4f}")
print(f"🔍 Mean Optimization Score at Top-K 25: {mean_opt_score_25:.4f}")
print(f"🔍 Mean Optimization Score at Top-K 10: {mean_opt_score_10:.4f}")
print(f"🏆 Best Top-K to Proceed With: {results['better_top_k']}")
