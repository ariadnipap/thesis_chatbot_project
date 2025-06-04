import json
import os
import pandas as pd

# File paths
top_p_088_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_p/evaluation/evaluation_results_60.json"
top_p_07_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_p/evaluation/evaluation_results_top_p_0.7.json"
top_p_055_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_p/evaluation/evaluation_results_top_p_0.55.json"
output_file = "/home/ariadnipap/thesis_chatbot_project/data/eval/top_p/stats/optimization_comparison.json"

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

# Compute Relevance (average of answer and context relevance)
df_088["relevance"] = (df_088["answer_relevance_score"] + df_088["context_relevance_score"]) / 2
df_07["relevance"] = (df_07["answer_relevance_score"] + df_07["context_relevance_score"]) / 2
df_055["relevance"] = (df_055["answer_relevance_score"] + df_055["context_relevance_score"]) / 2

# Compute Optimization Score
def compute_optimization_score(df):
    return (
        0.5 * df["faithfulness_score"] +
        0.25 * df["relevance"] +
        0.25 * df["groundedness_score"]
    )

df_088["optimization_score"] = compute_optimization_score(df_088)
df_07["optimization_score"] = compute_optimization_score(df_07)
df_055["optimization_score"] = compute_optimization_score(df_055)

# Compute Mean Optimization Score for Each Top-P Value
mean_opt_score_088 = df_088["optimization_score"].mean()
mean_opt_score_07 = df_07["optimization_score"].mean()
mean_opt_score_055 = df_055["optimization_score"].mean()

# Determine the best Top-P value
best_top_p = max([(0.88, mean_opt_score_088), (0.7, mean_opt_score_07), (0.55, mean_opt_score_055)], key=lambda x: x[1])[0]

# Store results
results = {
    "top_p_0.88": mean_opt_score_088,
    "top_p_0.7": mean_opt_score_07,
    "top_p_0.55": mean_opt_score_055,
    "better_top_p": best_top_p
}

# Save results to JSON
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

# Print the best Top-P value
print(f"✅ Optimization comparison completed. Results saved in: {output_file}")
print(f"🔍 Mean Optimization Score at Top-P 0.88: {mean_opt_score_088:.4f}")
print(f"🔍 Mean Optimization Score at Top-P 0.7: {mean_opt_score_07:.4f}")
print(f"🔍 Mean Optimization Score at Top-P 0.55: {mean_opt_score_055:.4f}")
print(f"🏆 Best Top-P to Proceed With: {results['better_top_p']}")
