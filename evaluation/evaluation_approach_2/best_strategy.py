import os
import json
import re
import numpy as np

# Directory containing evaluation result JSONs for Approach 2
EVAL_DIR = "/home/ariadnipap/thesis_chatbot_project/evaluation/evaluation_approach_2/evaluation_with_preprocessing/"

# Parse configuration from filename
def parse_config(filename):
    if "no_chunking" in filename:
        match = re.match(r"evaluation_results_(\d+)_([0-9.]+)_no_chunking\.json", filename)
        if match:
            return int(match.group(1)), float(match.group(2)), "no_chunking"
    else:
        match = re.match(r"evaluation_results_(\d+)_([0-9.]+)_chunked_(\d+)_(\d+)\.json", filename)
        if match:
            chunk = f"chunked_{match.group(3)}_{match.group(4)}"
            return int(match.group(1)), float(match.group(2)), chunk
    return None

# Load all evaluation scores and compute mean
def load_scores():
    score_map = {}
    for filename in os.listdir(EVAL_DIR):
        if not filename.endswith(".json"):
            continue
        config = parse_config(filename)
        if not config:
            continue
        with open(os.path.join(EVAL_DIR, filename), "r") as f:
            data = json.load(f)
            scores = [entry.get("evaluation_score") for entry in data if isinstance(entry.get("evaluation_score"), (int, float))]
            if scores:
                mean_score = round(np.mean(scores), 2)
                score_map[config] = mean_score
    return score_map

# Generate result JSON
def generate_result_json(score_map):
    sorted_scores = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    best_config, best_score = sorted_scores[0]
    scores_json = {
        "scores": {
            f"top_k={k}_top_p={p}_chunking={c}": s for (k, p, c), s in sorted_scores
        },
        "best_setting": f"top_k={best_config[0]}_top_p={best_config[1]}_chunking={best_config[2]}",
        "best_score": best_score
    }
    return scores_json

# Main execution
score_map = load_scores()
result_json = generate_result_json(score_map)

# Save JSON to file
with open("approach2_results.json", "w") as f:
    json.dump(result_json, f, indent=2)
