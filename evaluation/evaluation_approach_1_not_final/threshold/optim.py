import json
import os
import pandas as pd

# File paths
threshold_8_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/threshold/evaluation/evaluation_results_60.json"
threshold_3_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/threshold/evaluation/evaluation_results_threshold_-3.0_60.json"
output_file = "/home/ariadnipap/thesis_chatbot_project/data/eval/threshold/stats/optimization_comparison.json"

# Load JSON files
with open(threshold_8_path, "r", encoding="utf-8") as f:
    data_8 = json.load(f)

with open(threshold_3_path, "r", encoding="utf-8") as f:
    data_3 = json.load(f)

# Convert to DataFrame
df_8 = pd.DataFrame(data_8)
df_3 = pd.DataFrame(data_3)

# Compute Relevance (average of answer and context relevance)
df_8["relevance"] = (df_8["answer_relevance_score"] + df_8["context_relevance_score"]) / 2
df_3["relevance"] = (df_3["answer_relevance_score"] + df_3["context_relevance_score"]) / 2

# Compute Optimization Score
def compute_optimization_score(df):
    return (
        0.5 * df["faithfulness_score"] +
        0.25 * df["relevance"] +
        0.25 * df["groundedness_score"]
    )

df_8["optimization_score"] = compute_optimization_score(df_8)
df_3["optimization_score"] = compute_optimization_score(df_3)

# Compute Mean Optimization Score for Each Threshold
mean_opt_score_8 = df_8["optimization_score"].mean()
mean_opt_score_3 = df_3["optimization_score"].mean()

# Store results
results = {
    "threshold_-8": mean_opt_score_8,
    "threshold_-3": mean_opt_score_3,
    "better_threshold": "-3" if mean_opt_score_3 > mean_opt_score_8 else "-8"
}

# Save results to JSON
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

# Print the best threshold
print(f"✅ Optimization comparison completed. Results saved in: {output_file}")
print(f"🔍 Mean Optimization Score at Threshold -8: {mean_opt_score_8:.4f}")
print(f"🔍 Mean Optimization Score at Threshold -3: {mean_opt_score_3:.4f}")
print(f"🏆 Best Threshold to Proceed With: {results['better_threshold']}")
