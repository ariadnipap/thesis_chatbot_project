import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the JSON data
file_path = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_results.json"

with open(file_path, "r") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Select only numerical columns
numeric_columns = [
    "retrieval_time", "reranker_time", "response_time",
    "faithfulness_score", "answer_relevance_score", "context_relevance_score",
    "groundedness_score", "bleu", "rouge-l", "bertscore",
    "precision@k", "f1_score"
]

df_numeric = df[numeric_columns]

# Compute the correlation matrix
correlation_matrix = df_numeric.corr()

# Save the correlation matrix as a CSV file for easier viewing
correlation_matrix_path = "/home/ariadnipap/thesis_chatbot_project/data/correlation_matrix.csv"
correlation_matrix.to_csv(correlation_matrix_path, index=True)

# Create a heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Heatmap of Evaluation Metrics")

# Save the heatmap as a PNG file
heatmap_path = "/home/ariadnipap/thesis_chatbot_project/data/correlation_heatmap.png"
plt.savefig(heatmap_path, dpi=300, bbox_inches="tight")

# Print paths for easy access
print(f"✅ Correlation matrix saved to: {correlation_matrix_path}")
print(f"✅ Heatmap saved to: {heatmap_path}")
