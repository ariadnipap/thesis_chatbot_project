import os
import re
import json

def parse_xindex_file(file_path):
    """
    Parse the xindex.md file and extract metadata for each issue.
    """
    metadata_list = []
    issue_regex = re.compile(
        r"<b>Issue Number:</b>\s*([\w\-/#]+)<br>\s*"
        r"Description:\s*(.+?)<br>\s*"
        r"Keywords:\s*(.*?)<br>\s*"
        r"Owner:\s*(.*?)<br>\s*"
        r"Date:\s*(\d+)<br>\s*"
        r"Status:\s*(.+?)<br>\s*"
        r"Info:\s*\[info\]\((.+?)\)<br>",
        re.DOTALL,
    )

    with open(file_path, "r") as file:
        content = file.read()

    matches = issue_regex.findall(content)
    if not matches:
        print("No matches found in xindex.md")
    else:
        print(f"Found {len(matches)} issues in xindex.md")

    for match in matches:
        metadata = {
            "Issue Number": match[0].strip(),
            "Description": match[1].strip(),
            "Keywords": [kw.strip() for kw in match[2].split(",")],
            "Owner": match[3].strip(),
            "Date": match[4].strip(),
            "Status": match[5].strip(),
            "Info": match[6].strip(),
        }
        metadata_list.append(metadata)

    return metadata_list


def extract_detail(content):
    """
    Extract fields like Description, Actions Taken, Affected Systems, and Action Points from the file content.
    """
    field_patterns = {
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

    extracted_data = {}
    for field, pattern in field_patterns.items():
        match = re.search(pattern, content, re.DOTALL)
        if match:
            extracted_data[field] = match.group(1).strip()
        else:
            extracted_data[field] = "Not specified"

    return extracted_data


def parse_md_files(metadata_list, base_path):
    """
    Parse the issue files and extract detailed information, including individual fields.
    """
    for metadata in metadata_list:
        # Add 'X' prefix to the file name
        file_path = os.path.join(base_path, metadata["Info"])
        directory, file_name = os.path.split(file_path)
        file_name_with_x = f"X{file_name}"  
        updated_file_path = os.path.join(directory, file_name_with_x)

        try:
            with open(updated_file_path, "r") as file:
                content = file.read()
                # Extract detailed fields from the content
                detailed_fields = extract_detail(content)
                metadata["Detailed Description"] = detailed_fields
        except FileNotFoundError:
            print(f"File not found: {updated_file_path}")
            metadata["Detailed Description"] = {
                "Description": "Not specified",
                "Actions Taken": "Not specified",
                "Affected Systems": "Not specified",
                "Action Points": "Not specified",
            }

    return metadata_list


def main():
    """
    Main function to parse the xindex.md file, process issue files, and save results to JSON.
    """
    xindex_path = "data/raw_english/xindex.md"
    base_issue_path = "data/raw_english/"
    output_path = "data/processed/issues_english.json"

    print("Parsing xindex.md...")
    metadata_list = parse_xindex_file(xindex_path)

    print("Parsing issue files...")
    processed_data = parse_md_files(metadata_list, base_issue_path)

    print("Saving processed data to JSON...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as json_file:
        json.dump(processed_data, json_file, indent=4, ensure_ascii=False)

    print(f"Processing complete. Data saved to {output_path}")


if __name__ == "__main__":
    main()