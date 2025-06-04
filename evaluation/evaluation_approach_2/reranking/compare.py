import json
import matplotlib.pyplot as plt

# File paths
file1_path = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/reranking/evaluation_results_50_0.88_no_chunking_no_reranking.json"
file2_path = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/evaluation_with_preprocessing/evaluation_results_50_0.88_no_chunking.json"

# Normalization function
def normalize_1_to_5(score):
    return (score - 1) / 4 * 100

# Load JSON data
with open(file1_path, "r", encoding="utf-8") as f1:
    data1 = json.load(f1)

with open(file2_path, "r", encoding="utf-8") as f2:
    data2 = json.load(f2)

# Extract and normalize evaluation scores
scores1 = [normalize_1_to_5(item["evaluation_score"]) for item in data1 if "evaluation_score" in item]
scores2 = [normalize_1_to_5(item["evaluation_score"]) for item in data2 if "evaluation_score" in item]

# Calculate means
mean1 = sum(scores1) / len(scores1)
mean2 = sum(scores2) / len(scores2)

print(f"Normalized Mean Evaluation Score (no_reranking): {mean1:.2f}")
print(f"Normalized Mean Evaluation Score (with_reranking): {mean2:.2f}")

# Plotting
labels = ['No Reranking', 'With Reranking']
means = [mean1, mean2]

plt.figure(figsize=(6, 4))
plt.bar(labels, means, color=['skyblue', 'lightgreen'])
plt.ylim(0, 100)
plt.ylabel('Mean Score (0–100)')
plt.title('Normalized Mean Evaluation Score Comparison')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/reranking/mean_score_comparison_normalized.png")
plt.close()
