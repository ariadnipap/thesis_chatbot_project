# this code generates a large config file with all the data we want to include in the external database
import json
import os

# Directories containing markdown files
abc_app_flows_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/abc/applicationFlows"
abc_procedures_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/abc/procedures"
abc_issues_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/abc/issues"

mno_app_flows_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/mno/applicationFlows"
mno_procedures_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/mno/procedures"
mno_issues_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/mno/issues"

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

# Load all markdown data
abc_application_flows = load_markdown_files(abc_app_flows_dir)
abc_procedures = load_markdown_files(abc_procedures_dir)
abc_issues = load_markdown_files(abc_issues_dir)

mno_application_flows = load_markdown_files(mno_app_flows_dir)
mno_procedures = load_markdown_files(mno_procedures_dir)
mno_issues = load_markdown_files(mno_issues_dir)

# Construct the final JSON structure
config_data = {
    "bigstreamer_docs": {
        "applicationFlows": {
            "Client_abc": abc_application_flows,
            "Client_mno": mno_application_flows
        },
        "procedures": {
            "Client_abc": abc_procedures,
            "Client_mno": mno_procedures
        },
        "issues": {
            "Client_abc": abc_issues,
            "Client_mno": mno_issues
        }
    }
}

# Save to a single JSON file
config_path = "/home/ariadnipap/thesis_chatbot_project/data/processed/config_data.json"
with open(config_path, "w", encoding="utf-8") as json_file:
    json.dump(config_data, json_file, indent=4, ensure_ascii=False)

print(f"Configuration file saved at: {config_path}")