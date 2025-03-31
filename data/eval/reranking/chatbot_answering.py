import json
import time
from chatbot_english import chatbot_response  # Import chatbot function

# Load the evaluation dataset
EVAL_DATASET_PATH = "/home/ariadnipap/thesis_chatbot_project/data/qna/qna_new_60.json"
OUTPUT_FILE = "/home/ariadnipap/thesis_chatbot_project/data/answers_stats_no_reranking.json"

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