import os
import json
import re

# Directory for bb issues
bb_issues_dir = "/home/ariadnipap/thesis_chatbot_project/data/raw/bb/BigStreamer/issues"
output_json_path = "/home/ariadnipap/thesis_chatbot_project/data/processed/processed_bb_issues.json"

# Define expected issue fields and their corresponding regex patterns
ISSUE_FIELDS = {
    "Description": r"<b>Description:</b>\s*(.*?)\s*(<b>|$)",
    "Actions Taken": r"<b>Actions Taken:</b>\s*(.*?)\s*(<b>|$)",
    "Affected Systems": r"<b>Affected Systems:</b>\s*(.*?)\s*(<b>|$)",
    "Action Points": r"<b>Action Points:</b>\s*(.*?)\s*(<b>|$)",
    "Customer Update": r"<b>Customer Update:</b>\s*(.*?)\s*(<b>|$)",
    "Our Ticket Response": r"<b>Our Ticket Response:</b>\s*(.*?)\s*(<b>|$)",
    "Resolution": r"<b>Resolution:</b>\s*(.*?)\s*(<b>|$)",
    "Recommendations": r"<b>Recommendations:</b>\s*(.*?)\s*(<b>|$)",
    "Root Cause Analysis": r"<b>Root Cause Analysis:</b>\s*(.*?)\s*(<b>|$)",
    "Investigation": r"<b>Investigation:</b>\s*(.*?)\s*(<b>|$)",
    "References": r"<b>References:</b>\s*(.*?)\s*(<b>|$)",
    "Nfgh": r"<b>Nfgh:</b>\s*(.*?)\s*(<b>|$)",
}

def extract_issues_from_markdown(md_content):
    """
    Extracts issue fields from markdown content using regex patterns.
    """
    extracted_data = {}
    
    for field, pattern in ISSUE_FIELDS.items():
        match = re.search(pattern, md_content, re.DOTALL | re.IGNORECASE)
        extracted_data[field] = match.group(1).strip() if match else ""

    return extracted_data

def process_bb_issues():
    """
    Processes all issues for client 'bb' and saves them in a JSON file.
    """
    output_data = {}

    if not os.path.exists(bb_issues_dir):
        print(f"Directory {bb_issues_dir} not found. Exiting...")
        return

    for filename in os.listdir(bb_issues_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(bb_issues_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            extracted_data = extract_issues_from_markdown(md_content)
            output_data[filename] = extracted_data

    # Save output as JSON
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(output_data, json_file, indent=4, ensure_ascii=False)

    print(f"Processed bb issues. JSON saved at: {output_json_path}")

# Run the processing function
process_bb_issues()
