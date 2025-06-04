# use this code to test multiple configuration settings at once
import json
import time
import os

# Paths
CONFIG_PATH = "/home/ariadnipap/thesis_chatbot_project/scripts/config.json"
EVAL_DATASET_PATH = "/home/ariadnipap/thesis_chatbot_project/data/qna2/evaluation_dataset_with_context_good.json"
OUTPUT_DIR = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/answers_with_preprocessing/"

# Load evaluation questions
def load_evaluation_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Save results
def save_results(results, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

# Update config file
def update_config(top_k, top_p, chunk_setting):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Special handling for "no_chunking"
    if chunk_setting == "no_chunking":
        config["paths"]["faiss_index"] = "data/faiss_index_new/"
    else:
        config["paths"]["faiss_index"] = f"data/faiss_index_{chunk_setting}/"

    config["model_parameters"]["top_k"] = top_k
    config["model_parameters"]["top_p"] = top_p

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

# Evaluate chatbot
def evaluate_chatbot(dataset):
    from chatbot_english import chatbot_response

    results = []
    total = len(dataset["qa_pairs"])
    for idx, entry in enumerate(dataset["qa_pairs"], 1):
        print(f"🟡 [{idx}/{total}] Evaluating: {entry['question'][:80]}...")

        question = entry["question"]
        expected_answer = entry["answer"]
        context = entry.get("context", "")
        category = entry.get("category", "Unknown")

        start_time = time.time()
        chatbot_reply, retrieved_context, retrieval_time, reranker_time = chatbot_response(
            question, rag_enabled=True
        )
        end_time = time.time()

        results.append({
            "question": question,
            "category": category,
            "expected_answer": expected_answer,
            "context": context,
            "chatbot_response": chatbot_reply,
            "retrieved_context": retrieved_context,
            "retrieval_time": retrieval_time,
            "reranker_time": reranker_time,
            "response_time": end_time - start_time
        })

    return results

# Main execution
if __name__ == "__main__":
    dataset = load_evaluation_data(EVAL_DATASET_PATH)

    # Define chunking modes
    chunk_settings = ["no_chunking"]

    # Define top_k, top_p combinations
    combinations = [(50, 0.88)]

    for chunk_setting in chunk_settings:
        print(f"\n🔵 Starting evaluations for chunk setting: {chunk_setting}")

        for top_k, top_p in combinations:
            print(f"\n🚀 Running evaluation for top_k = {top_k}, top_p = {top_p}")
            update_config(top_k, top_p, chunk_setting)
            results = evaluate_chatbot(dataset)
            output_file = os.path.join(
                OUTPUT_DIR, f"answers_stats_{top_k}_{top_p}_{chunk_setting}_no_reranking.json" #change!!!
            )
            save_results(results, output_file)
            print(f"✅ Results saved to {output_file}")