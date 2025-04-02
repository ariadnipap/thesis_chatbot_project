# this code generates the embeddings + faiss index of the large config file with all the data and stores it in the output directory
# you can use any embedding model you like. here we have used mpnet base v2 and minilm l6 v2
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore import InMemoryDocstore
from langchain.schema import Document
import os

# Define FAISS index path
faiss_index_path = "/home/ariadnipap/thesis_chatbot_project/data/faiss_index_mpnet_chunked_500_100"

# Load JSON configuration file
config_path = "/home/ariadnipap/thesis_chatbot_project/data/processed/chunked_config_500_100.json"
with open(config_path, "r", encoding="utf-8") as f:
    config_data = json.load(f)

# Initialize Sentence Transformer model
#embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Function to extract text content from JSON
def extract_text_from_config(config):
    documents = []
    metadata_list = {}
    
    for category, clients in config["bigstreamer_docs"].items():
        for client, entries in clients.items():
            if isinstance(entries, list):  # Ensure it is a list of data entries
                for entry in entries:
                    if isinstance(entry, dict) and "content" in entry:
                        text = entry["content"]
                        metadata = {"category": category, "client": client, "name": entry.get("name", "unknown")}
                        doc_id = len(documents)  # Assign doc ID
                        documents.append(text)
                        metadata_list[doc_id] = Document(page_content=text, metadata=metadata)

    return documents, metadata_list

# Extract documents and metadata
documents, metadata_dict = extract_text_from_config(config_data)

# Generate embeddings
print("Generating embeddings for the extracted documents...")
embeddings = embedding_model.encode(documents, convert_to_numpy=True)

# Create FAISS index
dimension = embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(dimension)
faiss_index.add(embeddings)

# Store metadata with LangChain FAISS wrapper
vector_store = FAISS(
    #embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"),
    index=faiss_index,
    docstore=InMemoryDocstore(metadata_dict),  # Ensure metadata is stored
    index_to_docstore_id={i: i for i in range(len(documents))}
)

# Ensure output directory exists
os.makedirs(faiss_index_path, exist_ok=True)

# Save FAISS index
vector_store.save_local(faiss_index_path)

# Manually save docstore and index-to-docstore mapping
with open(os.path.join(faiss_index_path, "docstore_chunked.json"), "w", encoding="utf-8") as f:
    json.dump({k: {"page_content": v.page_content, "metadata": v.metadata} for k, v in metadata_dict.items()}, f, indent=4)

with open(os.path.join(faiss_index_path, "index_to_docstore_id_chunked.json"), "w", encoding="utf-8") as f:
    json.dump({i: i for i in range(len(documents))}, f, indent=4)

print(f"FAISS index successfully created and saved at: {faiss_index_path}")
