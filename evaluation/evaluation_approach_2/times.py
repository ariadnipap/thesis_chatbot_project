import json
import matplotlib.pyplot as plt
import numpy as np

# Path to your JSON file
file_path = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/answers_with_preprocessing/answers_stats_50_0.88_no_chunking.json"

# Load data
with open(file_path, "r") as f:
    data = json.load(f)

# Extract timing fields
retrieval_times = [item["retrieval_time"] for item in data]
reranker_times = [item["reranker_time"] for item in data]
response_times = [item["response_time"] for item in data]

# Compute statistics
mean_values = [
    np.mean(retrieval_times),
    np.mean(reranker_times),
    np.mean(response_times)
]

min_values = {
    "retrieval_time": np.min(retrieval_times),
    "reranker_time": np.min(reranker_times),
    "response_time": np.min(response_times)
}

max_values = {
    "retrieval_time": np.max(retrieval_times),
    "reranker_time": np.max(reranker_times),
    "response_time": np.max(response_times)
}

# Print min/max results
print("🔍 Min/Max Runtime Statistics:")
for key in min_values:
    print(f"{key}: min = {min_values[key]:.3f}s, max = {max_values[key]:.3f}s")

# Plot mean values
labels = ['Retrieval', 'Reranker', 'LLM Response']
colors = ['#4e79a7', '#f28e2b', '#e15759']

plt.figure(figsize=(8, 6))
bars = plt.bar(labels, mean_values, color=colors)
plt.ylabel("Mean Time (seconds)")
plt.title("Mean Runtime per Component (50 QAs, top_k=50, top_p=0.88, no_chunking)")

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.2f}", ha='center', va='bottom')

plt.tight_layout()
plt.savefig("/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/plots-results/runtime_breakdown.png", dpi=300)
plt.show()
