# test pipeline that implemented double reranking layer using a smaller llama model as a second reranker
import json
import os
import torch
import faiss
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import LlamaCpp
from langchain.schema import Document
from langchain.prompts import PromptTemplate

# ✅ Load Configuration from JSON
CONFIG_PATH = "/home/ariadnipap/thesis_chatbot_project/scripts/config.json"

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"⚠️ Configuration file {CONFIG_PATH} not found!")

with open(CONFIG_PATH, "r") as config_file:
    config = json.load(config_file)

FAISS_INDEX_PATH = config["paths"]["faiss_index"]
LLAMA_SMALL_PATH = "/home/ariadnipap/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf"
LLAMA_BIG_PATH = config["paths"]["llama_model"]
MODEL_PARAMS = config["model_parameters"]
RETRIEVAL_PARAMS = config["retrieval_settings"]

# ✅ Load FAISS index
print("📥 Loading FAISS index...")
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

if not os.path.exists(os.path.join(FAISS_INDEX_PATH, "index.pkl")):
    raise FileNotFoundError("⚠️ FAISS index not found! Make sure embeddings are generated.")

vector_store = FAISS.load_local(
    FAISS_INDEX_PATH, 
    embedding_model,
    allow_dangerous_deserialization=True
)

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": RETRIEVAL_PARAMS["k"]})

# ✅ Load Cross-Encoder Reranking Model
cross_encoder_model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
tokenizer = AutoTokenizer.from_pretrained(cross_encoder_model_name)
cross_encoder_model = AutoModelForSequenceClassification.from_pretrained(cross_encoder_model_name)
device = "cuda" if torch.cuda.is_available() else "cpu"
cross_encoder_model.to(device).eval()

# ✅ Load LLaMA Models with Updated Context Size
print("🚀 Loading Small LLaMA model (Relevance Scorer & Condenser)...")
llm_small = LlamaCpp(
    model_path=LLAMA_SMALL_PATH, 
    n_gpu_layers=0, 
    temperature=0.1, 
    max_tokens=2048,  # Increase max tokens
    n_ctx=8000  # Extended context length
)

print(f"🛠️ LLaMA Model Config: Max Tokens={llm_small.max_tokens}, Context Length={llm_small.n_ctx}")

print("🚀 Loading Large LLaMA model (Final Answer Generator)...")
llm_big = LlamaCpp(model_path=LLAMA_BIG_PATH, **MODEL_PARAMS)

# ✅ Cross-Encoder Reranking Function (Same as Before)
def rank_passages(query, passages, model, tokenizer, device):
    pairs = [[query, passage] for passage in passages]
    inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors="pt").to(device)

    with torch.no_grad():
        scores = model(**inputs).logits.squeeze(-1).tolist()

    ranked_results = sorted(zip(passages, scores), key=lambda x: x[1], reverse=True)
    print("\n🔍 Ranked Passages:")
    for passage, score in ranked_results:
        print(f"📜 Score: {score:.4f} | {passage[:200]}...")
    return ranked_results

import re

def score_with_llama8b(query, passages, model):
    """Scores full passages using LLaMA-8B with a relevance explanation and a 1-100 scale, with re-prompting for format correction."""
    scored_passages = []

    print("\n🔍 LLaMA-8B Scoring Each Passage (Full Documents):\n")

    for passage in passages:
        print(f"\n📝 Processing Full Passage: {passage[:200]}...\n")

        prompt = f"""
        You are an AI model trained to evaluate the relevance of a passage to a given query.  
        Your task is to assess how well the passage answers the query and assign a **relevance score from 1 to 100**.

        ### Scoring Guidelines:
        - A score **close to 100** means the passage **directly and fully answers** the query.
        - A score **around 50** means the passage is **related to the query** but does not fully answer it.
        - A score **close to 0** means the passage is **completely unrelated** to the query.

        ### Steps to Follow:
        1. **Extract key information from the query** – Identify what is being asked.
        2. **Analyze the passage** – Determine if it provides a direct, partial, or indirect answer.
        3. **Assign a relevance score** – Justify your score with a brief explanation.

        ---
        **Query:**  
        {query}

        **Passage:**  
        {passage}

        ---
        **Response Format (STRICTLY FOLLOW THE TEMPLATE BELOW IN YOUR RESPONSE):**  
        

        Relevance Score: X/100  
        Explanation: (Provide a short justification)


        """

        print("\n🚀 Sending This Prompt to LLaMA-8B:\n", repr(prompt))

        attempt = 0
        max_attempts = 2  # Limit re-prompting to 2 tries
        score = 0.0  # Default score if parsing fails

        while attempt < max_attempts:
            try:
                response = model.invoke(prompt, temperature=0.1, max_tokens=150, top_p=0.5)

                # 🔎 Debugging prints
                print(f"📜 Full Passage: {passage[:200]}...\n📝 Full LLaMA Response (Attempt {attempt+1}): '{response}'")

                if not response.strip():
                    print(f"⚠️ Empty response from LLaMA for passage: {passage[:200]}... Retrying.")
                    attempt += 1
                    continue

                # Extracting score using regex (supports variations with bold/italic formatting)
                match = re.search(r"[\*\_]*\s*Relevance Score:\s*[\*\_]*\s*(100|[1-9]?\d)\b", response.strip())

                if match:
                    score = float(match.group(1))  # Convert to float
                    print(f"✅ Parsed Score: {score}")
                    break  # Exit loop if parsing is successful
                else:
                    print(f"⚠️ No valid score found in response: {response.strip()}")

            except ValueError:
                print(f"⚠️ Failed to parse score from response: {response.strip()}")

            # If the format is incorrect, re-prompt with a stricter clarification
            prompt = f"""
            Your previous response did not match the required format. **Please strictly follow the response template and score the passage above based on relevance to the user query**:
            

            Relevance Score: X/100  
            Explanation: (Provide a short justification)


            ---
            **Query:**  
            {query}

            **Passage:**  
            {passage}
            """
            attempt += 1

        # Ensure score is within valid range
        if score < 0 or score > 100:
            print(f"⚠️ Invalid score {score}, setting to 0")
            score = 0.0

        scored_passages.append((passage, score))

    return sorted(scored_passages, key=lambda x: x[1], reverse=True)

# ✅ Chatbot Response Function (Now Uses Full Documents)
def chatbot_response(user_input, rag_enabled=False, temperature=None, max_tokens=None, top_p=None):
    if not isinstance(user_input, str):
        return "⚠️ Invalid input format."

    print("\n🔍 Query:", repr(user_input))

    temperature = temperature if temperature is not None else MODEL_PARAMS["temperature"]
    max_tokens = max_tokens if max_tokens is not None else MODEL_PARAMS["max_tokens"]
    top_p = top_p if top_p is not None else MODEL_PARAMS["top_p"]

    if rag_enabled:
        # 1️⃣ FAISS Retrieval (Retrieve **10** documents)
        try:
            retrieved_docs = retriever.invoke(user_input)
        except Exception as e:
            return "⚠️ Retrieval failed."

        retrieved_texts = [doc.page_content for doc in retrieved_docs]
        print(f"\n🛠️ Retrieved {len(retrieved_texts)} Documents Before Reranking.")

        if not retrieved_texts:
            return "⚠️ No relevant information found."

        # 2️⃣ Cross-Encoder Reranking (Keep **Top 5** documents)
        ranked_passages = rank_passages(user_input, retrieved_texts, cross_encoder_model, tokenizer, device)
        top_reranked_passages = [p[0] for p in ranked_passages[:5]]  # Keep top 5

        print(f"\n🔍 Retained Top {len(top_reranked_passages)} Passages After Reranking.")

        # 3️⃣ LLaMA-8B Full Document Scoring (Keep only those with **score ≥ 80**)
        filtered_passages = score_with_llama8b(user_input, top_reranked_passages, llm_small)
        high_score_passages = [p[0] for p in filtered_passages if p[1] >= 80]

        print(f"\n🔍 Retained {len(high_score_passages)} Passages with Score ≥ 80.")

        # 4️⃣ Context Trimming (Limit to max_chars)
        final_context = ""
        char_count = 0
        final_passages = []

        for passage in high_score_passages:
            if char_count + len(passage) <= RETRIEVAL_PARAMS["max_chars"]:
                final_passages.append(passage)
                char_count += len(passage)
            else:
                break  # Stop when max_chars is reached

        final_context = "\n".join(final_passages)
        print(f"\n🧐 Final Context Sent to LLaMA-70B ({char_count}/{RETRIEVAL_PARAMS['max_chars']} characters).")

    else:
        final_context = "No context provided."

    # 5️⃣ Final Answer Generation
    final_prompt = f"""
    You are an AI assistant. Use the provided knowledge to answer the question.

    Context:
    {final_context}

    Question:
    {user_input}

    Answer:
    """

    print("\n🚀 Final Prompt to LLaMA-70B:\n", final_prompt[:1000])

    try:
        response = llm_big.invoke(final_prompt, temperature=temperature, max_tokens=max_tokens, top_p=top_p)
    except Exception as e:
        return "⚠️ Model generation failed."

    print("\n💬 LLaMA-70B Response:", response)
    return response

if __name__ == "__main__":
    while True:
        user_input = input("\n🔍 Enter query (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        response = chatbot_response(user_input, rag_enabled=True)
        print("\n💬 Chatbot Response:\n", response)
