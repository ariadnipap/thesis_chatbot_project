import json
import os
import pandas as pd

# File paths for embedding model evaluation results
emb_model_1_path = "/home/ariadnipap/thesis_chatbot_project/data/eval_after_filter/emb_model/evaluation/evaluation_results_10_0.7_1000_200_new.json"
emb_model_2_path = "/home/ariadnipap/thesis_chatbot_project/data/eval_after_filter/emb_model/evaluation/evaluation_results_10_0.7_1000_200_mpnet.json"
output_file = "/home/ariadnipap/thesis_chatbot_project/data/eval_after_filter/emb_model/stats/optimization_comparison_emb_model.json"

# Load JSON files
with open(emb_model_1_path, "r", encoding="utf-8") as f:
    data_model_1 = json.load(f)

with open(emb_model_2_path, "r", encoding="utf-8") as f:
    data_model_2 = json.load(f)

# Convert to DataFrame
df_model_1 = pd.DataFrame(data_model_1)
df_model_2 = pd.DataFrame(data_model_2)

# Compute Relevance (average of answer and context relevance)
df_model_1["relevance"] = (df_model_1["answer_relevance_score"] + df_model_1["context_relevance_score"]) / 2
df_model_2["relevance"] = (df_model_2["answer_relevance_score"] + df_model_2["context_relevance_score"]) / 2

# Compute Optimization Score
def compute_optimization_score(df):
    return (
        0.5 * df["faithfulness_score"] +
        0.25 * df["relevance"] +
        0.25 * df["groundedness_score"]
    )

df_model_1["optimization_score"] = compute_optimization_score(df_model_1)
df_model_2["optimization_score"] = compute_optimization_score(df_model_2)

# Compute Mean Optimization Score for Each Model
mean_opt_score_model_1 = df_model_1["optimization_score"].mean()
mean_opt_score_model_2 = df_model_2["optimization_score"].mean()

# Determine the best embedding model
best_embedding_model = "MiniLM" if mean_opt_score_model_1 > mean_opt_score_model_2 else "MPNet"

# Store results
results = {
    "MiniLM": mean_opt_score_model_1,
    "MPNet": mean_opt_score_model_2,
    "better_embedding_model": best_embedding_model
}

# Save results to JSON
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

# Print the best embedding model
print(f"✅ Optimization comparison completed. Results saved in: {output_file}")
print(f"🔍 Mean Optimization Score for MiniLM: {mean_opt_score_model_1:.4f}")
print(f"🔍 Mean Optimization Score for MPNet: {mean_opt_score_model_2:.4f}")
print(f"🏆 Best Embedding Model to Proceed With: {results['better_embedding_model']}")
