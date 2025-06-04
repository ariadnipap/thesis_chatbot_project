import json
import os
import matplotlib.pyplot as plt
import numpy as np

# Directories and Files
DATA_DIR = "/home/ariadnipap/thesis_chatbot_project/evaluation/evaluation_approach_1/evaluation_with_preprocessing"
CHUNKING_TYPES = ["0", "1000_100", "2000_200"]

# Evaluation metrics to plot (faithfulness removed)
metrics = [
    "answer_relevance_score",
    "context_relevance_score",
    "groundedness_score",
    "bleu",
    "rouge-l",
    "bertscore",
]

# Metrics that should be normalized from 1–5 to 0–100
normalize_metrics = {
    "answer_relevance_score",
    "context_relevance_score",
    "groundedness_score",
}

# Store results
results = {chunking: {} for chunking in CHUNKING_TYPES}

# Load each file and aggregate results
for filename in os.listdir(DATA_DIR):
    if not filename.startswith("evaluation_results_") or not filename.endswith(".json"):
        continue

    for chunking in CHUNKING_TYPES:
        if filename.endswith(f"{chunking}.json"):
            parts = filename.replace("evaluation_results_", "").replace(f"_{chunking}.json", "").split("_")
            if len(parts) < 2:
                continue
            top_k, top_p = parts[0], parts[1]
            key = f"k={top_k}, p={top_p}"

            file_path = os.path.join(DATA_DIR, filename)
            with open(file_path, "r") as f:
                data = json.load(f)

            # Average metrics across entries
            metric_means = {}
            for metric in metrics:
                metric_values = [entry[metric] for entry in data if metric in entry and isinstance(entry[metric], (int, float))]
                if metric_values:
                    avg = sum(metric_values) / len(metric_values)
                    if metric in normalize_metrics:
                        avg = (avg - 1) / 4 * 100  # Normalize to [0, 100]
                    metric_means[metric] = avg
                else:
                    metric_means[metric] = 0

            results[chunking][key] = metric_means

# Plotting
for metric in metrics:
    labels = sorted(set.intersection(*(set(results[chunking].keys()) for chunking in CHUNKING_TYPES)))
    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(14, 6))

    # Bar values for each chunking type
    offsets = [-width, 0, width]
    colors = ["#1f77b4", "#2ca02c", "#d62728"]
    legends = ["No Chunking", "Chunking 1000-100", "Chunking 2000-200"]

    for i, chunking in enumerate(CHUNKING_TYPES):
        vals = [results[chunking][label][metric] for label in labels]
        ax.bar(x + offsets[i], vals, width, label=legends[i], color=colors[i])

    ax.set_ylabel(metric.replace("-", " ").capitalize() + (" (0-100)" if metric in normalize_metrics else ""))
    ax.set_title(f'{metric.replace("-", " ").capitalize()} by top_k and top_p (Filtered ≥ 4, Normalized)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()

    plt.tight_layout()
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)

    # Save to same directory or custom path
    output_path = f"/home/ariadnipap/thesis_chatbot_project/evaluation/evaluation_approach_1/normalized-plots-results/metric_plot_{metric}.png"
    plt.savefig(output_path)
    print(f"✅ Saved: {output_path}")
    plt.close()
