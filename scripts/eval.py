'''
import json
import os
import time
import pandas as pd
import torch
import numpy as np
import re
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
from evaluate import load
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate

# ✅ Load Configuration from JSON
CONFIG_PATH = "/home/ariadnipap/thesis_chatbot_project/scripts/config.json"

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"⚠️ Configuration file {CONFIG_PATH} not found!")

try:
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    required_keys = ["paths", "model_parameters"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"⚠️ Missing required key: '{key}' in {CONFIG_PATH}. Please check your configuration.")

    if "llama_model" not in config["paths"]:
        raise KeyError("⚠️ Missing 'llama_model' in 'paths'. Check config.json.")

except json.JSONDecodeError:
    raise ValueError(f"⚠️ Error reading {CONFIG_PATH}. Please ensure it is valid JSON.")

# ✅ Read paths and parameters from config.json
LLAMA_MODEL_PATH = "/home/ariadnipap/Llama-3.3-70B-Instruct-Q4_K_M.gguf"
MODEL_PARAMS = config["model_parameters"]

# ✅ Load evaluation metrics
bleu = load("sacrebleu")
rouge = load("rouge")
bertscore = load("bertscore")

# ✅ Load Sentence Transformer for semantic similarity
similarity_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ✅ Load Llama Model (Llama 3.3 70B GGUF)
print("🚀 Loading Llama-3.3-70B model...")
llm = LlamaCpp(
    model_path=LLAMA_MODEL_PATH,
    **MODEL_PARAMS
)

# ✅ Define LLM Evaluation Prompt
EVALUATION_PROMPT = """You are an expert AI judge evaluating chatbot responses.
Your task is to compare the given chatbot response with the reference answer.
Follow the guidelines below and provide a **detailed assessment** followed by a **score** between 1 and 5.

### **Instruction (Question):**
{instruction}

### **Chatbot Response:**
{response}

### **Reference Answer (Score 5):**
{reference_answer}

### **Scoring Criteria:**
1️⃣ **Score 1**: Completely incorrect or irrelevant.
2️⃣ **Score 2**: Mostly incorrect or contains major factual errors.
3️⃣ **Score 3**: Partially correct but missing key details.
4️⃣ **Score 4**: Mostly correct with minor inaccuracies.
5️⃣ **Score 5**: Fully correct and well-articulated.

### **Final Output Format:**
1️⃣ **Feedback:** (Explain why you gave this score.)
2️⃣ **[RESULT]** (Final Score between 1 and 5)

Now, analyze and provide your evaluation.
"""

prompt_template = PromptTemplate(
    input_variables=["instruction", "response", "reference_answer"],
    template=EVALUATION_PROMPT
)

# ✅ Utility Functions
def normalize_text(text):
    """Lowercases, removes punctuation, and strips spaces."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text

def compute_f1(prediction, reference):
    """Computes F1 score between predicted and reference answer."""
    pred_tokens = set(normalize_text(prediction).split())
    ref_tokens = set(normalize_text(reference).split())

    common_tokens = pred_tokens & ref_tokens
    if len(common_tokens) == 0:
        return 0

    precision = len(common_tokens) / len(pred_tokens)
    recall = len(common_tokens) / len(ref_tokens)
    return 2 * (precision * recall) / (precision + recall)

def compute_similarity(text1, text2):
    """Computes cosine similarity between two texts using embeddings."""
    embedding1 = similarity_model.encode(text1, convert_to_tensor=True)
    embedding2 = similarity_model.encode(text2, convert_to_tensor=True)
    return util.pytorch_cos_sim(embedding1, embedding2).item()

def evaluate_response(question, chatbot_answer, ground_truth_answer):
    """Uses Llama-3.3-70B as a judge to evaluate chatbot responses."""
    
    # Generate evaluation prompt
    eval_prompt = prompt_template.format(
        instruction=question,
        response=chatbot_answer,
        reference_answer=ground_truth_answer,
    )
    
    # Get LLaMA's evaluation
    eval_result = llm.invoke(eval_prompt)

    # ✅ Log full LLaMA response for debugging
    print("\n📜 DEBUG: LLaMA Raw Response:\n", eval_result)

    # ✅ Extract score from LLaMA response using regex
    match = re.search(r"\*\*Score:\s*([1-5])\*\*", eval_result)
    
    if match:
        faithfulness_score = int(match.group(1))  # Extract score as an integer
        feedback = eval_result.split("### **[RESULT]**")[0].strip()  # Keep only the feedback section
    else:
        faithfulness_score = 1  # Default to 1 if parsing fails
        feedback = "Error in parsing feedback"

    return feedback, faithfulness_score, eval_result  # Returning full raw response

# ✅ Load test dataset
QA_DATASET_PATH = "/home/ariadnipap/thesis_chatbot_project/data/chatbot_answers/test1_test.json"
with open(QA_DATASET_PATH, "r") as f:
    qa_data = json.load(f)

qa_df = pd.DataFrame(qa_data)

# ✅ Store results
results = []

print("🚀 Running chatbot and evaluating responses...")
for i, row in tqdm(qa_df.iterrows(), total=len(qa_df)):
    question = row["question"]
    ground_truth_answer = row["expected_answer"]
    chatbot_answer = row["chatbot_response"]
    response_time = row["response_time"]

    # ✅ Compute Traditional Metrics
    bleu_score = bleu.compute(predictions=[chatbot_answer], references=[[ground_truth_answer]])["score"]
    rouge_score = rouge.compute(predictions=[chatbot_answer], references=[ground_truth_answer])
    bertscore_value = bertscore.compute(predictions=[chatbot_answer], references=[ground_truth_answer], model_type="distilbert-base-uncased")["f1"][0]

    # ✅ Compute Recall@K and Precision@K using similarity
    recall_k = compute_similarity(ground_truth_answer, chatbot_answer) > 0.5
    precision_k = compute_similarity(ground_truth_answer, chatbot_answer)
    
    # ✅ Compute F1 Score
    f1 = compute_f1(chatbot_answer, ground_truth_answer)

    # ✅ LLM-Based Evaluation
    feedback, faithfulness_score, llm_raw_response = evaluate_response(question, chatbot_answer, ground_truth_answer)

    # ✅ Store results
    results.append({
        "question": question,
        "ground_truth": ground_truth_answer,
        "chatbot_answer": chatbot_answer,
        "response_time": response_time,
        "faithfulness_score": faithfulness_score,  # Now correctly extracted
        "judge_feedback": feedback,  # Now contains only feedback text
        "llm_raw_response": llm_raw_response,  # Stores full LLaMA output
        "bleu": bleu_score,
        "rouge-l": rouge_score["rougeL"],
        "bertscore": bertscore_value,
        "recall@k": recall_k,
        "precision@k": precision_k,
        "f1_score": f1
    })

# ✅ Save results
RESULTS_PATH = "/home/ariadnipap/thesis_chatbot_project/data/final_evaluation_results5.json"
with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=4)

import gc
del llm  # Delete model instance
gc.collect()  # Force memory cleanup

print(f"✅ Evaluation Completed! Results saved to {RESULTS_PATH}")
'''



import json
import os
import time
import pandas as pd
import torch
import numpy as np
import re
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
from evaluate import load
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate

# ✅ Load Configuration from JSON
CONFIG_PATH = "/home/ariadnipap/thesis_chatbot_project/scripts/config.json"

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"⚠️ Configuration file {CONFIG_PATH} not found!")

try:
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    required_keys = ["paths", "model_parameters"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"⚠️ Missing required key: '{key}' in {CONFIG_PATH}. Please check your configuration.")

    if "llama_model" not in config["paths"]:
        raise KeyError("⚠️ Missing 'llama_model' in 'paths'. Check config.json.")

except json.JSONDecodeError:
    raise ValueError(f"⚠️ Error reading {CONFIG_PATH}. Please ensure it is valid JSON.")

# ✅ Read paths and parameters from config.json
LLAMA_MODEL_PATH = "/home/ariadnipap/Llama-3.3-70B-Instruct-Q4_K_M.gguf"
MODEL_PARAMS = config["model_parameters"]

# ✅ Load evaluation metrics
bleu = load("sacrebleu")
rouge = load("rouge")
bertscore = load("bertscore")

# ✅ Load Sentence Transformer for semantic similarity
similarity_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ✅ Load Llama Model (Llama 3.3 70B GGUF)
print("🚀 Loading Llama-3.3-70B model...")
llm = LlamaCpp(
    model_path=LLAMA_MODEL_PATH,
    **MODEL_PARAMS
)

def normalize_text(text):
    """Lowercases, removes punctuation, and strips spaces."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text

def compute_f1(prediction, reference):
    """Computes F1 score between predicted and reference answer."""
    pred_tokens = set(normalize_text(prediction).split())
    ref_tokens = set(normalize_text(reference).split())

    common_tokens = pred_tokens & ref_tokens
    if len(common_tokens) == 0:
        return 0

    precision = len(common_tokens) / len(pred_tokens)
    recall = len(common_tokens) / len(ref_tokens)
    return 2 * (precision * recall) / (precision + recall)

def compute_similarity(text1, text2):
    """Computes cosine similarity between two texts using embeddings."""
    embedding1 = similarity_model.encode(text1, convert_to_tensor=True)
    embedding2 = similarity_model.encode(text2, convert_to_tensor=True)
    return util.pytorch_cos_sim(embedding1, embedding2).item()

# ✅ Define LLM Evaluation Prompts
EVALUATION_PROMPT = """You are an expert AI judge evaluating chatbot responses.
Your task is to compare the given chatbot response with the reference answer.
Follow the guidelines below and provide a **detailed assessment** followed by a **score** between 1 and 5.

### **Instruction (Question):**
{instruction}

### **Chatbot Response:**
{response}

### **Reference Answer (Score 5):**
{reference_answer}

### **Scoring Criteria:**
1️⃣ **Score 1**: Completely incorrect or irrelevant.
2️⃣ **Score 2**: Mostly incorrect or contains major factual errors.
3️⃣ **Score 3**: Partially correct but missing key details.
4️⃣ **Score 4**: Mostly correct with minor inaccuracies.
5️⃣ **Score 5**: Fully correct and well-articulated.

### **Final Output Format:**
1️⃣ **Feedback:** (Explain why you gave this score.)
2️⃣ **[RESULT]** (Final Score between 1 and 5)

Now, analyze and provide your evaluation.
"""

ANSWER_RELEVANCE_PROMPT = """You are an expert AI judge evaluating chatbot responses.
Your task is to assess whether the chatbot's response is relevant to the given query.
Follow the guidelines below and provide a **detailed assessment** followed by a **score** between 1 and 5.

### **Instruction (Query):**
{instruction}

### **Chatbot Response:**
{response}

### **Scoring Criteria:**
1️⃣ **Score 1**: Completely irrelevant to the query.
2️⃣ **Score 2**: Mostly irrelevant or off-topic.
3️⃣ **Score 3**: Somewhat relevant but missing key elements.
4️⃣ **Score 4**: Mostly relevant with minor gaps.
5️⃣ **Score 5**: Fully relevant and directly answers the query.

### **Final Output Format:**
1️⃣ **Feedback:** (Explain why you gave this score.)
2️⃣ **[RESULT]** (Final Score between 1 and 5)

Now, analyze and provide your evaluation.
"""

CONTEXT_RELEVANCE_PROMPT = """You are an expert AI judge evaluating chatbot responses.
Your task is to assess whether the **retrieved context** is relevant to the given query.
Follow the guidelines below and provide a **detailed assessment** followed by a **score** between 1 and 5.

### **Instruction (Query):**
{instruction}

### **Retrieved Context:**
{retrieved_context}

### **Scoring Criteria:**
1️⃣ **Score 1**: Completely irrelevant to the query.
2️⃣ **Score 2**: Mostly irrelevant or off-topic.
3️⃣ **Score 3**: Somewhat relevant but missing key elements.
4️⃣ **Score 4**: Mostly relevant with minor gaps.
5️⃣ **Score 5**: Fully relevant and provides necessary information.

### **Final Output Format:**
1️⃣ **Feedback:** (Explain why you gave this score.)
2️⃣ **[RESULT]** (Final Score between 1 and 5)

Now, analyze and provide your evaluation.
"""

GROUNDEDNESS_PROMPT = """You are an expert AI judge evaluating chatbot responses.
Your task is to assess whether the chatbot's response is **well-supported** by the retrieved context.
Follow the guidelines below and provide a **detailed assessment** followed by a **score** between 1 and 5.

### **Instruction (Query):**
{instruction}

### **Retrieved Context:**
{retrieved_context}

### **Chatbot Response:**
{response}

### **Scoring Criteria:**
1️⃣ **Score 1**: No grounding in the retrieved context.
2️⃣ **Score 2**: Barely grounded, mostly unrelated.
3️⃣ **Score 3**: Somewhat grounded, but with significant gaps.
4️⃣ **Score 4**: Mostly grounded with minor issues.
5️⃣ **Score 5**: Fully grounded, well-supported by context.

### **Final Output Format:**
1️⃣ **Feedback:** (Explain why you gave this score.)
2️⃣ **[RESULT]** (Final Score between 1 and 5)

Now, analyze and provide your evaluation.
"""

# ✅ Utility Function to Truncate Text by Removing Last 800 Tokens
def truncate_text(text, num_tokens_to_remove=800, avg_chars_per_token=3.5):
    """Removes the last num_tokens_to_remove tokens from the text."""
    if not text or len(text) < num_tokens_to_remove * avg_chars_per_token:
        return text  # Return as is if it's already short

    truncated_length = int(len(text) - (num_tokens_to_remove * avg_chars_per_token))
    truncated_text = text[:truncated_length].rstrip()  # Ensure no trailing spaces
    return truncated_text

# ✅ Utility Function for Evaluation
def evaluate_with_llama(prompt_template, instruction, response=None, retrieved_context=None, reference_answer=None, truncate_context=False):
    """Uses LLaMA-3.3-70B to evaluate chatbot responses based on a given prompt.
    
    - If `truncate_context=True`, it removes 800 tokens from the **end** of the retrieved context.
    """

    # ✅ Apply truncation only when evaluating **Groundedness** or **Context Relevance**
    if truncate_context and retrieved_context:
        retrieved_context = truncate_text(retrieved_context, num_tokens_to_remove=800)

    # ✅ Generate evaluation prompt based on required fields
    eval_prompt = prompt_template.format(
        instruction=instruction,
        response=response if response else "",
        retrieved_context=retrieved_context if retrieved_context else "",
        reference_answer=reference_answer if reference_answer else ""
    )

    eval_result = llm.invoke(eval_prompt)
    
    print("\n📜 DEBUG: LLaMA Raw Response:\n", eval_result)

    # ✅ Improved regex for score extraction (handles multiple formats)
    match = re.search(r"(?:Score[:\s]*|[Rr]esult[:\s]*|\*\*Score\*\*\s*|The final answer is:\s*\$\\boxed{)([1-5])", eval_result)
    
    if match:
        score = int(match.group(1)) if match.group(1) else int(match.group(2))
    else:
        score = "Error in parsing score"  # ✅ If no match, explicitly note the error

    # ✅ Store **full raw response** in the feedback fields for manual review
    return eval_result, score, eval_result

'''
# ✅ Load test dataset
QA_DATASET_PATH = "/home/ariadnipap/thesis_chatbot_project/data/answers_stats_50_0.7_500_100.json"
with open(QA_DATASET_PATH, "r") as f:
    qa_data = json.load(f)

qa_df = pd.DataFrame(qa_data)

# ✅ Store results
results = []

print("🚀 Running chatbot and evaluating responses...")
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
    bertscore_value = bertscore.compute(predictions=[chatbot_answer], references=[ground_truth_answer], model_type="distilbert-base-uncased")["f1"][0]
    
    recall_k = compute_similarity(ground_truth_answer, chatbot_answer) > 0.5
    precision_k = compute_similarity(ground_truth_answer, chatbot_answer)
    f1 = compute_f1(chatbot_answer, ground_truth_answer)

    # ✅ LLM-Based Evaluations
    feedback_faithfulness, faithfulness_score, raw_faithfulness = evaluate_with_llama(
        EVALUATION_PROMPT, question, chatbot_answer, retrieved_context=None, reference_answer=ground_truth_answer
    )

    feedback_ans_rel, answer_rel_score, raw_ans_rel = evaluate_with_llama(
        ANSWER_RELEVANCE_PROMPT, question, chatbot_answer, retrieved_context=None, reference_answer=None
    )

    feedback_ctx_rel, context_rel_score, raw_ctx_rel = evaluate_with_llama(
        CONTEXT_RELEVANCE_PROMPT, question, retrieved_context=retrieved_context, reference_answer=None, truncate_context=True  # ✅ Truncate Context
    )

    feedback_grounded, groundedness_score, raw_grounded = evaluate_with_llama(
        GROUNDEDNESS_PROMPT, question, chatbot_answer, retrieved_context=retrieved_context, reference_answer=None, truncate_context=True  # ✅ Truncate Context
    )

    # ✅ Store results
    results.append({
        "question": question,
        "category": category,
        "ground_truth": ground_truth_answer,
        "chatbot_answer": chatbot_answer,
        "retrieved_context": retrieved_context,
        "retrieval_time": retrieval_time,
        "reranker_time": reranker_time,
        "response_time": response_time,
        "faithfulness_score": faithfulness_score,
        "answer_relevance_score": answer_rel_score,
        "context_relevance_score": context_rel_score,
        "groundedness_score": groundedness_score,
        "judge_feedback_faithfulness": raw_faithfulness,
        "judge_feedback_answer_relevance": raw_ans_rel,
        "judge_feedback_context_relevance": raw_ctx_rel,
        "judge_feedback_groundedness": raw_grounded,
        "bleu": bleu_score,
        "rouge-l": rouge_score["rougeL"],
        "bertscore": bertscore_value,
        "recall@k": recall_k,
        "precision@k": precision_k,
        "f1_score": f1
    })


# ✅ Save results
RESULTS_PATH = "/home/ariadnipap/thesis_chatbot_project/data/evaluation_results_50_0.7_500_100.json"
with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=4)

import gc
del llm  # Delete model instance
gc.collect()  # Force memory cleanup

print(f"✅ Evaluation Completed! Results saved to {RESULTS_PATH}")
'''

# Add this at the top
import gc

# Wrap the evaluation logic in a function
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
        bertscore_value = bertscore.compute(predictions=[chatbot_answer], references=[ground_truth_answer], model_type="distilbert-base-uncased")["f1"][0]

        recall_k = compute_similarity(ground_truth_answer, chatbot_answer) > 0.5
        precision_k = compute_similarity(ground_truth_answer, chatbot_answer)
        f1 = compute_f1(chatbot_answer, ground_truth_answer)

        feedback_faithfulness, faithfulness_score, raw_faithfulness = evaluate_with_llama(
            EVALUATION_PROMPT, question, chatbot_answer, retrieved_context=None, reference_answer=ground_truth_answer
        )
        feedback_ans_rel, answer_rel_score, raw_ans_rel = evaluate_with_llama(
            ANSWER_RELEVANCE_PROMPT, question, chatbot_answer, retrieved_context=None
        )
        feedback_ctx_rel, context_rel_score, raw_ctx_rel = evaluate_with_llama(
            CONTEXT_RELEVANCE_PROMPT, question, retrieved_context=retrieved_context, truncate_context=True
        )
        feedback_grounded, groundedness_score, raw_grounded = evaluate_with_llama(
            GROUNDEDNESS_PROMPT, question, chatbot_answer, retrieved_context=retrieved_context, truncate_context=True
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
            "faithfulness_score": faithfulness_score,
            "answer_relevance_score": answer_rel_score,
            "context_relevance_score": context_rel_score,
            "groundedness_score": groundedness_score,
            "judge_feedback_faithfulness": raw_faithfulness,
            "judge_feedback_answer_relevance": raw_ans_rel,
            "judge_feedback_context_relevance": raw_ctx_rel,
            "judge_feedback_groundedness": raw_grounded,
            "bleu": bleu_score,
            "rouge-l": rouge_score["rougeL"],
            "bertscore": bertscore_value,
            "recall@k": recall_k,
            "precision@k": precision_k,
            "f1_score": f1
        })

    # ✅ Save results
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"✅ Evaluation Completed! Results saved to {output_file}")


# ✅ List of files to evaluate
eval_files = [
    ("answers_stats_10_0.88_chunked_1000_200.json", "evaluation_results_10_0.88_1000_200.json"),
    ("answers_stats_10_0.7_chunked_1000_200.json", "evaluation_results_10_0.7_1000_200.json"),
    ("answers_stats_10_0.55_chunked_1000_200.json", "evaluation_results_10_0.55_1000_200.json"),
    ("answers_stats_25_0.55_chunked_1000_200.json", "evaluation_results_25_0.88_1000_200.json")
]

for input_filename, output_filename in eval_files:
    INPUT_PATH = f"/home/ariadnipap/thesis_chatbot_project/data/{input_filename}"
    OUTPUT_PATH = f"/home/ariadnipap/thesis_chatbot_project/data/{output_filename}"

    run_evaluation(INPUT_PATH, OUTPUT_PATH)

    # Cleanup memory between runs
    del llm
    gc.collect()

    # Reload model
    llm = LlamaCpp(model_path=LLAMA_MODEL_PATH, **MODEL_PARAMS)
