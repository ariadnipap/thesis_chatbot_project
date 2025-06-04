import json
import time
import os
from chatbot_english import chatbot_response  # Import chatbot function

# Load the evaluation dataset
EVAL_DATASET_PATH = "/home/ariadnipap/thesis_chatbot_project/data/qna/qna_new_60.json"
CONFIG_PATH = "/home/ariadnipap/thesis_chatbot_project/scripts/config.json"

# Define the `top_k` value to test
TOP_K_VALUE = 10  # ✅ Updated to test `top_k = 10`

# Function to load the dataset
def load_evaluation_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Function to update `top_k` in config.json
def update_config_top_k(config_path, new_top_k):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Update the `top_k` value
    config["model_parameters"]["top_k"] = new_top_k

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    print(f"✅ Updated `top_k` to {new_top_k} in config.json.")

# Function to evaluate chatbot with the new `top_k`
def evaluate_chatbot(dataset):
    results = []
    for entry in dataset["qa_pairs"]:
        question = entry["question"]
        expected_answer = entry["answer"]
        category = entry.get("category", "Unknown")  # ✅ Extract category

        start_time = time.time()
        chatbot_reply, retrieved_context, retrieval_time, reranker_time = chatbot_response(
            question, rag_enabled=True  # ✅ No need to pass `top_k`, it is read from config
        )
        end_time = time.time()
        
        response_time = end_time - start_time  # Total response time (including retrieval and reranking)

        results.append({
            "question": question,
            "category": category,  # ✅ Store category
            "expected_answer": expected_answer,
            "chatbot_response": chatbot_reply,
            "retrieved_context": retrieved_context,  # ✅ Store retrieved context
            "retrieval_time": retrieval_time,  # ✅ Store time taken by the retriever
            "reranker_time": reranker_time,  # ✅ Store time taken by the reranker
            "response_time": response_time,  # ✅ Store total time taken
            "top_k": TOP_K_VALUE  # ✅ Store the tested `top_k` value
        })
    
    return results

# Function to save results
def save_results(results, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    # Step 1: Update `top_k` in config.json
    update_config_top_k(CONFIG_PATH, TOP_K_VALUE)

    # Step 2: Reload dataset
    dataset = load_evaluation_data(EVAL_DATASET_PATH)

    # Step 3: Run chatbot evaluation
    output_file = f"/home/ariadnipap/thesis_chatbot_project/data/answers_stats_top_k_{TOP_K_VALUE}.json"
    print(f"\n🚀 Running chatbot evaluation with top_k = {TOP_K_VALUE} ...")
    results = evaluate_chatbot(dataset)
    save_results(results, output_file)
    print(f"✅ Evaluation completed for top_k = {TOP_K_VALUE}. Results saved to {output_file}")
