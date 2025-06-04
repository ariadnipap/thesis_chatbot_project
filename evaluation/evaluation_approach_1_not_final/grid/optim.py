import json
import os
import pandas as pd

# ✅ Directory where all evaluation files are stored
DATA_DIR = "/home/ariadnipap/thesis_chatbot_project/data/eval/grid/evaluation"
OUTPUT_FILE = os.path.join(DATA_DIR, "optimization_grid_results.json")

# ✅ Optimization function weights
def compute_optimization_score(df):
    df["relevance"] = (df["answer_relevance_score"] + df["context_relevance_score"]) / 2
    return (
        0.5 * df["faithfulness_score"] +
        0.25 * df["relevance"] +
        0.25 * df["groundedness_score"]
    )

# ✅ Collect optimization results from all files
results = {}

for filename in os.listdir(DATA_DIR):
    if not filename.startswith("evaluation_results_") or not filename.endswith(".json"):
        continue

    path = os.path.join(DATA_DIR, filename)

    try:
        parts = filename.replace("evaluation_results_", "").replace(".json", "").split("_")
        top_k, top_p = parts[0], parts[1]
        chunking = "0" if len(parts) == 3 else f"{parts[2]}_{parts[3]}"
    except Exception as e:
        print(f"⚠️ Skipping {filename}: couldn't parse parameters. Error: {e}")
        continue

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    required_columns = ["faithfulness_score", "answer_relevance_score", "context_relevance_score", "groundedness_score"]
    if not all(col in df.columns for col in required_columns):
        print(f"⚠️ Skipping {filename}: missing required metric columns.")
        continue

    df["optimization_score"] = compute_optimization_score(df)
    mean_score = df["optimization_score"].mean()

    config_key = f"top_k={top_k}_top_p={top_p}_chunking={chunking}"
    results[config_key] = mean_score

# ✅ Determine best setting
best_setting = max(results.items(), key=lambda x: x[1])

# ✅ Save all results
output = {
    "scores": results,
    "best_setting": best_setting[0],
    "best_score": best_setting[1]
}

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4)

print(f"✅ Optimization results saved to {OUTPUT_FILE}")
print(f"🏆 Best configuration: {best_setting[0]} with score: {best_setting[1]:.4f}")
