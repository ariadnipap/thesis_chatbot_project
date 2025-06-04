import json
import os
import pandas as pd

# File paths for chunking evaluation results
non_chunking_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/chunking/evaluation/evaluation_results_60.json"
chunking_500_path = "/home/ariadnipap/thesis_chatbot_project/data/eval/chunking/evaluation/evaluation_results_chunked.json"
output_file = "/home/ariadnipap/thesis_chatbot_project/data/eval/chunking/stats/optimization_comparison.json"

# Load JSON files
with open(non_chunking_path, "r", encoding="utf-8") as f:
    data_non_chunking = json.load(f)

with open(chunking_500_path, "r", encoding="utf-8") as f:
    data_chunking_500 = json.load(f)

# Convert to DataFrame
df_non_chunking = pd.DataFrame(data_non_chunking)
df_chunking_500 = pd.DataFrame(data_chunking_500)

# Compute Relevance (average of answer and context relevance)
df_non_chunking["relevance"] = (df_non_chunking["answer_relevance_score"] + df_non_chunking["context_relevance_score"]) / 2
df_chunking_500["relevance"] = (df_chunking_500["answer_relevance_score"] + df_chunking_500["context_relevance_score"]) / 2

# Compute Optimization Score
def compute_optimization_score(df):
    return (
        0.5 * df["faithfulness_score"] +
        0.25 * df["relevance"] +
        0.25 * df["groundedness_score"]
    )

df_non_chunking["optimization_score"] = compute_optimization_score(df_non_chunking)
df_chunking_500["optimization_score"] = compute_optimization_score(df_chunking_500)

# Compute Mean Optimization Score for Each Chunking Setting
mean_opt_score_non_chunking = df_non_chunking["optimization_score"].mean()
mean_opt_score_chunking_500 = df_chunking_500["optimization_score"].mean()

# Determine the better setting
best_chunking = "Chunking (500)" if mean_opt_score_chunking_500 > mean_opt_score_non_chunking else "No Chunking"

# Store results
results = {
    "non_chunking": mean_opt_score_non_chunking,
    "chunking_500": mean_opt_score_chunking_500,
    "better_chunking": best_chunking
}

# Save results to JSON
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

# Print the best chunking setting
print(f"✅ Optimization comparison completed. Results saved in: {output_file}")
print(f"🔍 Mean Optimization Score (No Chunking): {mean_opt_score_non_chunking:.4f}")
print(f"🔍 Mean Optimization Score (Chunking 500): {mean_opt_score_chunking_500:.4f}")
print(f"🏆 Best Chunking Strategy: {results['better_chunking']}")
