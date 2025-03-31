'''
import json
import time
from chatbot_english import chatbot_response  # Import chatbot function

# Load the evaluation dataset
EVAL_DATASET_PATH = "/home/ariadnipap/thesis_chatbot_project/data/qna/qna_new_60.json"
OUTPUT_FILE = "/home/ariadnipap/thesis_chatbot_project/data/answers_stats_10_0.55_500_100.json"

def load_evaluation_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_chatbot(dataset):
    results = []
    for entry in dataset["qa_pairs"]:
        question = entry["question"]
        expected_answer = entry["answer"]
        category = entry.get("category", "Unknown")  # ✅ Extract category (default to "Unknown" if missing)

        start_time = time.time()
        chatbot_reply, retrieved_context, retrieval_time, reranker_time = chatbot_response(question, rag_enabled=True)
        end_time = time.time()
        
        response_time = end_time - start_time  # Total response time (including retrieval and reranking)

        results.append({
            "question": question,
            "category": category,  # ✅ New field: store category
            "expected_answer": expected_answer,
            "chatbot_response": chatbot_reply,
            "retrieved_context": retrieved_context,  # ✅ Store retrieved context
            "retrieval_time": retrieval_time,  # ✅ Store time taken by the retriever
            "reranker_time": reranker_time,  # ✅ Store time taken by the reranker
            "response_time": response_time  # ✅ Store total time taken
        })
    
    return results

def save_results(results, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    dataset = load_evaluation_data(EVAL_DATASET_PATH)
    results = evaluate_chatbot(dataset)
    save_results(results, OUTPUT_FILE)
    print(f"✅ Evaluation completed. Results saved to {OUTPUT_FILE}")
'''

import json
import time
import os
from chatbot_english import chatbot_response

# Paths
CONFIG_PATH = "/home/ariadnipap/thesis_chatbot_project/scripts/config.json"
EVAL_DATASET_PATH = "/home/ariadnipap/thesis_chatbot_project/data/qna/qna_new_60.json"
OUTPUT_DIR = "/home/ariadnipap/thesis_chatbot_project/data"
CHUNK_SETTING = "chunked_1000_200"

# Load evaluation questions
def load_evaluation_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Evaluate chatbot
def evaluate_chatbot(dataset):
    results = []
    for entry in dataset["qa_pairs"]:
        question = entry["question"]
        expected_answer = entry["answer"]
        category = entry.get("category", "Unknown")

        start_time = time.time()
        chatbot_reply, retrieved_context, retrieval_time, reranker_time = chatbot_response(question, rag_enabled=True)
        end_time = time.time()

        results.append({
            "question": question,
            "category": category,
            "expected_answer": expected_answer,
            "chatbot_response": chatbot_reply,
            "retrieved_context": retrieved_context,
            "retrieval_time": retrieval_time,
            "reranker_time": reranker_time,
            "response_time": end_time - start_time
        })
    return results

# Save results
def save_results(results, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

# Update config file
def update_config(top_k, top_p):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    config["paths"]["faiss_index"] = f"data/faiss_index_{CHUNK_SETTING}/"
    config["model_parameters"]["top_k"] = top_k
    config["model_parameters"]["top_p"] = top_p

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

# Run evaluations
if __name__ == "__main__":
    dataset = load_evaluation_data(EVAL_DATASET_PATH)
    combinations = [(50, 0.88), (50, 0.7), (50, 0.55), (25, 0.88), (25, 0.7), (25, 0.55), (10, 0.88), (10, 0.7), (10, 0.55)]

    for top_k, top_p in combinations:
        print(f"\n🚀 Running evaluation for top_k = {top_k}, top_p = {top_p}")
        update_config(top_k, top_p)
        results = evaluate_chatbot(dataset)
        output_file = os.path.join(OUTPUT_DIR, f"answers_stats_{top_k}_{top_p}_{CHUNK_SETTING}.json")
        save_results(results, output_file)
        print(f"✅ Results saved to {output_file}")
