# evaluation code for the second evaluation approach
import json
import os
import gc
import re
import time
import pandas as pd
import torch
import numpy as np
from tqdm import tqdm
from evaluate import load
from sentence_transformers import SentenceTransformer, util
from langchain_community.llms import LlamaCpp

# === Load config ===
CONFIG_PATH = "/home/ariadnipap/thesis_chatbot_project/scripts/config.json"

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"⚠️ Configuration file {CONFIG_PATH} not found!")

with open(CONFIG_PATH, "r") as config_file:
    config = json.load(config_file)

LLAMA_MODEL_PATH = config["paths"]["llama_model"]
MODEL_PARAMS = config["model_parameters"]

# === Load metrics ===
bleu = load("sacrebleu")
rouge = load("rouge")
bertscore = load("bertscore")

similarity_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# === Load LLaMA model ===
print("🚀 Loading LLaMA model...")
llm = LlamaCpp(model_path=LLAMA_MODEL_PATH, **MODEL_PARAMS)

# === Utility functions ===
def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def compute_f1(prediction, reference):
    pred_tokens = set(normalize_text(prediction).split())
    ref_tokens = set(normalize_text(reference).split())

    common_tokens = pred_tokens & ref_tokens
    if len(common_tokens) == 0:
        return 0

    precision = len(common_tokens) / len(pred_tokens)
    recall = len(common_tokens) / len(ref_tokens)
    return 2 * (precision * recall) / (precision + recall)

def compute_similarity(text1, text2):
    embedding1 = similarity_model.encode(text1, convert_to_tensor=True)
    embedding2 = similarity_model.encode(text2, convert_to_tensor=True)
    return util.pytorch_cos_sim(embedding1, embedding2).item()

# === Unified Evaluation Prompt ===
SINGLE_EVAL_PROMPT = """
###Task Description: You will be given an instruction (might include an Input inside it), a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given.

1. Write a short feedback that assess the quality of the response strictly based on the given score rubric, not evaluating in general.
2. After writing a feedback, write a score that is an integer between 1 and 5. You should refer to the score rubric.
3. The output format should look as follows:
\"Feedback: {{write a feedback for criteria}} [RESULT] {{an integer number between 1 and 5}}\"
4. Please do not generate any other opening, closing, and explanations. Be sure to include [RESULT] in your output.

###The instruction to evaluate:
{instruction}

###Response to evaluate:
{response}

###Reference Answer (Score 5):
{reference_answer}

###Score Rubrics: [Is the response correct, accurate, and factual based on the reference answer?]
Score 1: The response is completely incorrect, inaccurate, and/or not factual.
Score 2: The response is mostly incorrect, inaccurate, and/or not factual.
Score 3: The response is somewhat correct, accurate, and/or factual.
Score 4: The response is mostly correct, accurate, and factual.
Score 5: The response is completely correct, accurate, and factual.

###Now provide your Feedback:
"""

def evaluate_with_single_score(instruction, response, reference_answer):
    prompt = SINGLE_EVAL_PROMPT.format(
        instruction=instruction,
        response=response,
        reference_answer=reference_answer
    )
    print("\n📝 EVALUATION PROMPT:\n", prompt)
    output = llm.invoke(prompt)
    print("\n📜 DEBUG LLaMA OUTPUT:\n", output)
    match = re.search(r"\[RESULT\]\s*(\d)", output)
    score = int(match.group(1)) if match else -1
    return output, score

# === Evaluation function ===
def run_evaluation(input_file, output_file):
    with open(input_file, "r") as f:
        qa_data = json.load(f)

    qa_df = pd.DataFrame(qa_data)
    results = []

    print(f"🚀 Running evaluation for {input_file}...")
    for i, row in tqdm(qa_df.iterrows(), total=len(qa_df)):
        question = row["question"]
        category = row["category"]
        ground_truth_answer = row["expected_answer"]
        chatbot_answer = row["chatbot_response"]
        retrieved_context = row["retrieved_context"]
        response_time = row["response_time"]
        retrieval_time = row["retrieval_time"]
        reranker_time = row["reranker_time"]

        bleu_score = bleu.compute(predictions=[chatbot_answer], references=[[ground_truth_answer]])["score"]
        rouge_score = rouge.compute(predictions=[chatbot_answer], references=[ground_truth_answer])
        bertscore_value = bertscore.compute(
            predictions=[chatbot_answer],
            references=[ground_truth_answer],
            model_type="distilbert-base-uncased"
        )["f1"][0]

        recall_k = compute_similarity(ground_truth_answer, chatbot_answer) > 0.5
        precision_k = compute_similarity(ground_truth_answer, chatbot_answer)
        f1 = compute_f1(chatbot_answer, ground_truth_answer)

        eval_feedback, eval_score = evaluate_with_single_score(
            instruction=question,
            response=chatbot_answer,
            reference_answer=ground_truth_answer
        )

        results.append({
            "question": question,
            "category": category,
            "ground_truth": ground_truth_answer,
            "chatbot_answer": chatbot_answer,
            "retrieved_context": retrieved_context,
            "retrieval_time": retrieval_time,
            "reranker_time": reranker_time,
            "response_time": response_time,
            "evaluation_score_feedback": eval_feedback,
            "evaluation_score": eval_score,
            "bleu": bleu_score,
            "rouge-l": rouge_score["rougeL"],
            "bertscore": bertscore_value,
            "recall@k": recall_k,
            "precision@k": precision_k,
            "f1_score": f1
        })

    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"✅ Evaluation Completed! Results saved to {output_file}")

# === Files to evaluate ===
eval_files = [
    #("answers_stats_10_0.55_no_chunking.json", "evaluation_results_10_0.55_no_chunking.json"),
    #("answers_stats_10_0.7_no_chunking.json", "evaluation_results_10_0.7_no_chunking.json"),
    #("answers_stats_10_0.88_no_chunking.json", "evaluation_results_10_0.88_no_chunking.json"),
    #("answers_stats_25_0.55_no_chunking.json", "evaluation_results_25_0.55_no_chunking.json"),
    #("answers_stats_25_0.7_no_chunking.json", "evaluation_results_25_0.7_no_chunking.json"),
    #("answers_stats_25_0.88_no_chunking.json", "evaluation_results_25_0.88_no_chunking.json"),
    #("answers_stats_50_0.55_no_chunking.json", "evaluation_results_50_0.55_no_chunking.json"),
    #("answers_stats_50_0.7_no_chunking.json", "evaluation_results_50_0.7_no_chunking.json"),
    ("answers_stats_50_0.88_no_chunking_no_reranking.json", "evaluation_results_50_0.88_no_chunking_no_reranking.json"),
    #("answers_stats_10_0.55_chunked_1000_100.json", "evaluation_results_10_0.55_chunked_1000_100.json"),
    #("answers_stats_10_0.7_chunked_1000_100.json", "evaluation_results_10_0.7_chunked_1000_100.json"),
    #("answers_stats_10_0.88_chunked_1000_100.json", "evaluation_results_10_0.88_chunked_1000_100.json"),
    #("answers_stats_25_0.55_chunked_1000_100.json", "evaluation_results_25_0.55_chunked_1000_100.json"),
    #("answers_stats_25_0.7_chunked_1000_100.json", "evaluation_results_25_0.7_chunked_1000_100.json"),
    #("answers_stats_25_0.88_chunked_1000_100.json", "evaluation_results_25_0.88_chunked_1000_100.json"),
    #("answers_stats_50_0.55_chunked_1000_100.json", "evaluation_results_50_0.55_chunked_1000_100.json"),
    #("answers_stats_50_0.7_chunked_1000_100.json", "evaluation_results_50_0.7_chunked_1000_100.json"),
    #("answers_stats_50_0.88_chunked_1000_100.json", "evaluation_results_50_0.88_chunked_1000_100.json"),
    #("answers_stats_10_0.55_chunked_2000_200.json", "evaluation_results_10_0.55_chunked_2000_200.json"),
    #("answers_stats_10_0.7_chunked_2000_200.json", "evaluation_results_10_0.7_chunked_2000_200.json"),
    #("answers_stats_10_0.88_chunked_2000_200.json", "evaluation_results_10_0.88_chunked_2000_200.json"),
    #("answers_stats_25_0.55_chunked_2000_200.json", "evaluation_results_25_0.55_chunked_2000_200.json"),
    #("answers_stats_25_0.7_chunked_2000_200.json", "evaluation_results_25_0.7_chunked_2000_200.json"),
    #("answers_stats_25_0.88_chunked_2000_200.json", "evaluation_results_25_0.88_chunked_2000_200.json"),
    #("answers_stats_50_0.55_chunked_2000_200.json", "evaluation_results_50_0.55_chunked_2000_200.json"),
    #("answers_stats_50_0.7_chunked_2000_200.json", "evaluation_results_50_0.7_chunked_2000_200.json"),
    #("answers_stats_50_0.88_chunked_2000_200.json", "evaluation_results_50_0.88_chunked_2000_200.json")
]


# === Run evaluation for each file ===
for input_filename, output_filename in eval_files:
    INPUT_PATH = f"/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/answers_with_preprocessing/{input_filename}"
    OUTPUT_PATH = f"/home/ariadnipap/thesis_chatbot_project/data/evaluation_approach_2/evaluation_with_preprocessing/{output_filename}"

    run_evaluation(INPUT_PATH, OUTPUT_PATH)

    del llm
    gc.collect()

    llm = LlamaCpp(model_path=LLAMA_MODEL_PATH, **MODEL_PARAMS)

print("🎉 All evaluations completed!")
