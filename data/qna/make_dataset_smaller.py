import json
import random
from collections import defaultdict

# File paths
qna_file_path = "/home/ariadnipap/thesis_chatbot_project/data/qna/qna_new.json"
output_qna_file = "/home/ariadnipap/thesis_chatbot_project/data/qna/qna_new_60.json"

# Load the Q&A dataset
with open(qna_file_path, "r", encoding="utf-8") as f:
    qna_data = json.load(f)

# Group questions by category
category_dict = defaultdict(list)
for qa in qna_data["qa_pairs"]:
    category_dict[qa["category"]].append(qa)

# Select 15 questions from each category (ensuring at most 15 if fewer exist)
selected_questions = []
for category, questions in category_dict.items():
    selected_questions.extend(random.sample(questions, min(15, len(questions))))  # Ensure max 15 per category

# Create the new Q&A JSON file
new_qna_data = {"qa_pairs": selected_questions}
with open(output_qna_file, "w", encoding="utf-8") as f:
    json.dump(new_qna_data, f, indent=4)

# Get the selected question texts for filtering other files
selected_question_texts = {qa["question"] for qa in selected_questions}

# List of chatbot answer files to process
evaluation_files = [
    "/home/ariadnipap/thesis_chatbot_project/data/answers_stats.json",
    "/home/ariadnipap/thesis_chatbot_project/data/answers_stats_test_threshold_-3.0.json",
    "/home/ariadnipap/thesis_chatbot_project/data/answers_stats_test_threshold_-5.0.json",
    "/home/ariadnipap/thesis_chatbot_project/data/evaluation_results.json",
    "/home/ariadnipap/thesis_chatbot_project/data/evaluation_results_threshold_-3.0.json"
]

# Process each file and keep only selected 60 questions
for file_path in evaluation_files:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter entries to keep only the selected questions
    filtered_data = [entry for entry in data if entry["question"] in selected_question_texts]

    # Generate new file name
    new_file_path = file_path.replace(".json", "_60.json")

    # Save the filtered data
    with open(new_file_path, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, indent=4)

print("✅ Filtering complete. New files created with '_60' suffix.")
