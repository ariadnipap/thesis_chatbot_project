import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Directory containing evaluation results
EVAL_DIR = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/evaluation_with_preprocessing/"

# Parse configuration from filename
def parse_config(filename):
    if "no_chunking" in filename:
        match = re.match(r"evaluation_results_(\d+)_([0-9.]+)_no_chunking\.json", filename)
        if match:
            return int(match.group(1)), float(match.group(2)), "no_chunking"
    else:
        match = re.match(r"evaluation_results_(\d+)_([0-9.]+)_chunked_(\d+)_(\d+)\.json", filename)
        if match:
            chunking = f"chunked_{match.group(3)}_{match.group(4)}"
            return int(match.group(1)), float(match.group(2)), chunking
    return None

# Collect all metric records
records = []

for fname in os.listdir(EVAL_DIR):
    if not fname.endswith(".json"):
        continue
    config = parse_config(fname)
    if not config:
        continue
    with open(os.path.join(EVAL_DIR, fname), "r") as f:
        data = json.load(f)
        for entry in data:
            if all(m in entry for m in ("bleu", "rouge-l", "bertscore", "f1_score")):
                records.append({
                    "top_k": config[0],
                    "top_p": config[1],
                    "chunking": config[2],
                    "bleu": entry["bleu"] * 100,
                    "rouge-l": entry["rouge-l"] * 100,
                    "bertscore": entry["bertscore"] * 100,
                    "f1_score": entry["f1_score"] * 100
                })

# Convert to DataFrame
df = pd.DataFrame(records)

# Compute mean metric scores per configuration
summary_df = df.groupby(["top_k", "top_p", "chunking"]).mean(numeric_only=True).reset_index()

# Reshape for plotting
melted_df = summary_df.melt(
    id_vars=["top_k", "top_p", "chunking"],
    value_vars=["bleu", "rouge-l", "bertscore", "f1_score"],
    var_name="metric", value_name="score"
)

# Format metric names for nicer display
metric_name_map = {
    "bleu": "BLEU",
    "rouge-l": "ROUGE-L",
    "bertscore": "BERTScore",
    "f1_score": "F1"
}
melted_df["metric"] = melted_df["metric"].map(metric_name_map)

# Plot with seaborn
sns.set(style="whitegrid")
g = sns.catplot(
    data=melted_df,
    x="metric", y="score", hue="chunking", col="top_k", row="top_p",
    kind="bar", height=3.5, aspect=1.2
)

# Final layout tweaks
g.fig.subplots_adjust(top=0.92)
g.fig.suptitle("Traditional Metrics Across Configurations (Normalized to 0–100)", fontsize=16)
g.set_axis_labels("Metric", "Score (0–100)")
g.set(ylim=(0, 100))

# Save and show
g.savefig("traditional_metrics_grid_normalized.png")
plt.show()
