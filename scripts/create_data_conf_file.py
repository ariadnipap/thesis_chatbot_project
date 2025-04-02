# this code generates a large config file with all the data we want to include in the external database
import json
import os

# add your files below
# Paths for structured issues
abc_issues_path = "/home/ariadnipap/thesis_chatbot_project/data/processed/processed_abc_issues.json"
bb_issues_path = "/home/ariadnipap/thesis_chatbot_project/data/processed/processed_bb_issues.json"

# Directories containing unstructured markdown files
abc_app_flows_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/abc_aa/applicationFlows"
abc_procedures_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/abc_aa/procedures"
bb_app_flows_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/bb/applicationFlows"
bb_procedures_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/bb/procedures"

# Load structured issues JSON files
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Read markdown files from a given directory
def load_markdown_files(directory):
    markdown_files = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".md"):
            file_path = os.path.join(directory, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            markdown_files.append({"name": file_name, "content": content})
    return markdown_files

# Load all data
abc_issues = load_json(abc_issues_path)
bb_issues = load_json(bb_issues_path)

abc_application_flows = load_markdown_files(abc_app_flows_dir)
abc_procedures = load_markdown_files(abc_procedures_dir)
bb_application_flows = load_markdown_files(bb_app_flows_dir)
bb_procedures = load_markdown_files(bb_procedures_dir)

# Construct the final JSON structure
config_data = {
    "bigstreamer_docs": {
        "applicationFlows": {
            "ClientA": abc_application_flows,
            "ClientB": bb_application_flows
        },
        "procedures": {
            "ClientA": abc_procedures,
            "ClientB": bb_procedures
        },
        "issues": {
            "ClientA": abc_issues,
            "ClientB": bb_issues
        }
    }
}

# Save to a single JSON file
config_path = "/home/ariadnipap/thesis_chatbot_project/data/processed/config_data.json"
with open(config_path, "w", encoding="utf-8") as json_file:
    json.dump(config_data, json_file, indent=4, ensure_ascii=False)

print(f"Configuration file saved at: {config_path}")
