# This code performs chunking of the large config file of the data using a recursive text splitter.
# It allows structured splitting based on newlines, spaces, punctuation, etc.

import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configurations
CHUNK_SIZE = 2000  # Number of tokens (or characters, if using default len)
OVERLAP = 200      # Overlapping tokens/chars for context retention

# File paths (Modify these paths if needed)
INPUT_FILE = "/home/ariadnipap/thesis_chatbot_project/data/processed/config_data.json"
OUTPUT_FILE = "/home/ariadnipap/thesis_chatbot_project/data/processed/chunked_config_2000_200.json"

# Load the JSON file
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"⚠️ Input file {INPUT_FILE} not found!")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Initialize Recursive Text Splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=OVERLAP,
    separators=["\n\n", "\n", ".", " ", ""],  # Best-effort split order
    keep_separator=True  # Optional: keep the delimiter in the chunk
)

# Process and Chunk Documents
chunked_docs = {"bigstreamer_docs": {}}

for category, clients in data.get("bigstreamer_docs", {}).items():
    chunked_docs["bigstreamer_docs"][category] = {}

    for client, documents in clients.items():
        # Skip "issues" category and copy it as-is
        if category == "issues":
            chunked_docs["bigstreamer_docs"][category][client] = documents
            continue

        chunked_docs["bigstreamer_docs"][category][client] = []

        for doc in documents:
            if not isinstance(doc, dict) or "content" not in doc:
                print(f"⚠️ Skipping invalid document in {category} -> {client}: {doc}")
                continue

            name = doc.get("name", "unknown")
            content = doc["content"]

            # Split the document content
            chunks = text_splitter.split_text(content)

            # Store each chunk as a separate document
            for i, chunk in enumerate(chunks):
                chunked_docs["bigstreamer_docs"][category][client].append({
                    "name": f"{name} - Part {i+1}",
                    "content": chunk
                })

# Save chunked documents to a new JSON file
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(chunked_docs, f, indent=4)

print(f"✅ Document chunking completed. Output saved to {OUTPUT_FILE}")
