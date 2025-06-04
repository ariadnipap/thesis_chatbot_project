import json
import time
from chatbot_english import chatbot_response  # Import chatbot function

# Load the evaluation dataset
EVAL_DATASET_PATH = "/home/ariadnipap/thesis_chatbot_project/data/qna/qna_new.json"

# Define the thresholds to test
THRESHOLDS = [-5.0, -3.0]

# Function to load the dataset
def load_evaluation_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Function to evaluate chatbot with a given threshold
def evaluate_chatbot(dataset, threshold):
    results = []
    for entry in dataset["qa_pairs"]:
        question = entry["question"]
        expected_answer = entry["answer"]
        category = entry.get("category", "Unknown")  # ✅ Extract category (default to "Unknown" if missing)

        start_time = time.time()
        chatbot_reply, retrieved_context, retrieval_time, reranker_time = chatbot_response(
            question, rag_enabled=True, threshold=threshold  # ✅ Pass threshold to chatbot
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
            "threshold": threshold  # ✅ Store the tested threshold value
        })
    
    return results

# Function to save results
def save_results(results, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    dataset = load_evaluation_data(EVAL_DATASET_PATH)

    for threshold in THRESHOLDS:
        output_file = f"/home/ariadnipap/thesis_chatbot_project/data/answers_stats_test_threshold_{threshold}.json"
        print(f"\n🚀 Running chatbot evaluation with threshold = {threshold} ...")
        results = evaluate_chatbot(dataset, threshold)
        save_results(results, output_file)
        print(f"✅ Evaluation completed for threshold = {threshold}. Results saved to {output_file}")