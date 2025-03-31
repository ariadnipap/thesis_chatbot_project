import json
import os
import faiss
import numpy as np
import torch
import time
import multiprocessing
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import LlamaCpp
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_huggingface import HuggingFaceEmbeddings

# ✅ Import Cross-Encoder
from sentence_transformers import CrossEncoder

# ✅ Load Configuration from JSON
CONFIG_PATH = "/home/ariadnipap/thesis_chatbot_project/scripts/config.json"

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"⚠️ Configuration file {CONFIG_PATH} not found!")

# ✅ Load the JSON file safely
try:
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    required_keys = ["paths", "model_parameters", "retrieval_settings"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"⚠️ Missing required key: '{key}' in {CONFIG_PATH}. Please check your configuration.")

    if "faiss_index" not in config["paths"] or "llama_model" not in config["paths"]:
        raise KeyError("⚠️ Missing 'faiss_index' or 'llama_model' in 'paths'. Check config.json.")

except json.JSONDecodeError:
    raise ValueError(f"⚠️ Error reading {CONFIG_PATH}. Please ensure it is valid JSON.")

# ✅ Read paths and parameters from config.json
FAISS_INDEX_PATH = config["paths"]["faiss_index"]
LLAMA_MODEL_PATH = config["paths"]["llama_model"]
MODEL_PARAMS = config["model_parameters"]
RETRIEVAL_PARAMS = config["retrieval_settings"]
PHOENIX_PORT=8080

# ✅ Load FAISS index
print("📥 Loading FAISS index...")

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

if not os.path.exists(os.path.join(FAISS_INDEX_PATH, "index.pkl")):
    raise FileNotFoundError("⚠️ FAISS index not found! Make sure embeddings are generated.")

vector_store = FAISS.load_local(
    FAISS_INDEX_PATH, 
    embedding_model,
    allow_dangerous_deserialization=True
)

# ✅ Load LLAMA model
print("🚀 Loading Llama model...")
llm = LlamaCpp(
    model_path=LLAMA_MODEL_PATH,
    **MODEL_PARAMS
)

# ✅ Load Cross-Encoder model for re-ranking
print("🎯 Loading Cross-Encoder model...")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
device = "cuda" if torch.cuda.is_available() else "cpu"
cross_encoder.to(device).eval()

# ✅ Define prompt template for LLaMA
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    You are an AI assistant. Use the provided knowledge to answer the question.

    Context: {context}
    Question: {question}
    Answer:
    """
)

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": RETRIEVAL_PARAMS["k"]}
)

def rerank_and_filter_documents(docs, user_query, threshold=None):
    """Re-rank and filter retrieved documents using Cross-Encoder."""

    # ✅ Get threshold from config if not provided dynamically
    if threshold is None:
        threshold = RETRIEVAL_PARAMS["threshold"]

    threshold = float(threshold)

    if not docs:
        return []

    # Prepare input for cross-encoder: list of (query, document) pairs
    input_pairs = [(user_query, doc.page_content) for doc in docs]

    # Compute relevance scores
    scores = cross_encoder.predict(input_pairs)

    # Pair documents with their scores
    scored_docs = list(zip(docs, scores))

    # Sort by score (descending order)
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    # Filter documents with scores above the threshold
    filtered_docs = [doc for doc, score in scored_docs if score >= threshold]

    print("\n🔍 DEBUG: Filtered Documents and Scores:")
    for doc, score in scored_docs:
        print(f"Score: {score:.2f} | {doc.page_content[:100]}...")

    return filtered_docs


def truncate_context_to_fit(documents, user_input, max_tokens, avg_chars_per_token=3.5, safety_buffer=200):
    """
    Truncates the document context to fit within the model's context size limit.

    - Ensures `user_input + system_prompt + context` fit within `max_tokens - safety_buffer`.
    - Truncates **only the last document** if needed, preserving earlier documents fully.
    - **Keeps new lines and formatting** intact.

    Args:
        documents (list): List of Document objects.
        user_input (str): The user's query.
        max_tokens (int): The model's maximum token limit.
        avg_chars_per_token (float): Estimated characters per token.
        safety_buffer (int): Tokens reserved to prevent exceeding the model's limit.

    Returns:
        str: Truncated context string.
    """

    # ✅ Step 1: Calculate estimated token usage
    user_query_tokens = len(user_input) / avg_chars_per_token  # Estimate tokens in user query
    system_prompt_tokens = 150  # Approximate system prompt length

    # ✅ Step 2: Determine available space for the context
    max_context_tokens = max_tokens - (user_query_tokens + system_prompt_tokens + safety_buffer)

    final_context = []
    current_tokens = 0

    for i, doc in enumerate(documents):
        doc_text = doc.page_content.strip()
        if not doc_text:
            continue

        estimated_tokens = len(doc_text) / avg_chars_per_token

        # ✅ If adding the full document exceeds the limit, truncate this one
        if current_tokens + estimated_tokens > max_context_tokens:
            allowed_chars = int((max_context_tokens - current_tokens) * avg_chars_per_token)
            
            # **Find a safe truncation point (end of a line)**
            truncated_text = doc_text[:allowed_chars]
            last_newline = truncated_text.rfind("\n")
            if last_newline != -1:
                truncated_text = truncated_text[:last_newline]  # Cut at last safe newline

            final_context.append(truncated_text)
            break  # Stop adding more documents

        # ✅ If it fits, add the full document
        final_context.append(doc_text)
        current_tokens += estimated_tokens

    # ✅ If no documents fit, include at least part of the first one
    if not final_context and documents:
        doc_text = documents[0].page_content
        allowed_chars = int(max_context_tokens * avg_chars_per_token)
        truncated_text = doc_text[:allowed_chars]

        # Cut at last safe newline
        last_newline = truncated_text.rfind("\n")
        if last_newline != -1:
            truncated_text = truncated_text[:last_newline]

        final_context.append(truncated_text)

    return "\n".join(final_context)  # Preserve new lines

def chatbot_response(user_input, rag_enabled=False, threshold=None, temperature=None, max_tokens=None, top_p=None):
    """Uses RAG pipeline with Cross-Encoder filtering before passing context to LLaMA."""

    start_time = time.time()  # Start measuring total latency

    # ✅ Get threshold from config if not provided
    if threshold is None:
        threshold = RETRIEVAL_PARAMS["threshold"]

    threshold = float(threshold)

    if not isinstance(user_input, str):
        print("⚠️ ERROR: user_input must be a string. Received:", type(user_input))
        return "⚠️ Invalid input format.", None, None, None  # Return placeholders

    print("\n🔍 Query before embedding:", repr(user_input))

    # ✅ Use default model parameters if not provided
    temperature = temperature if temperature is not None else MODEL_PARAMS["temperature"]
    max_tokens = max_tokens if max_tokens is not None else MODEL_PARAMS["max_tokens"]
    top_p = top_p if top_p is not None else MODEL_PARAMS["top_p"]

    if rag_enabled:
        try:
            retrieval_start_time = time.time()  # Start retrieval timing
            retrieved_docs = retriever.invoke(user_input)
            retrieval_end_time = time.time()  # End retrieval timing
        except Exception as e:
            print("⚠️ FAISS Retrieval Error:", str(e))
            return "⚠️ Retrieval failed.", None, None, None

        if not retrieved_docs:
            return "⚠️ No relevant information found in the knowledge base.", None, retrieval_end_time - retrieval_start_time, None

        retrieval_latency = retrieval_end_time - retrieval_start_time

        # ✅ Apply Cross-Encoder filtering using config threshold
        reranker_start_time = time.time()  # Start reranker timing
        filtered_docs = rerank_and_filter_documents(retrieved_docs, user_input, threshold)
        reranker_end_time = time.time()  # End reranker timing
        reranker_latency = reranker_end_time - reranker_start_time

        print("\n📜 DEBUG: Filtered Documents Before Truncation:")
        for doc in filtered_docs:
            print(f"{doc.page_content[:200]}...\n")

        # ✅ Ensure the context fits within LLaMA's context limit
        full_context = truncate_context_to_fit(
            filtered_docs,
            user_input,
            max_tokens=MODEL_PARAMS["n_ctx"] - 200,  # Apply 200-token safety buffer
            avg_chars_per_token=3.5
        )

        if not full_context.strip():
            full_context = "No relevant documents found."
    else:
        full_context = "No context provided."
        retrieval_latency = None
        reranker_latency = None

    final_prompt = f"""
    You are an AI assistant. Use the provided context to answer the question.

    Context:
    {full_context}

    Question:
    {user_input}

    Now give me your response to the question based on the context provided:
    """

    print("\n📜 DEBUG: Final Prompt Sent to LLaMA:\n", final_prompt, "...")

    try:
        generation_start_time = time.time()  # Start LLaMA generation timing
        response = llm.invoke(final_prompt, temperature=temperature, max_tokens=max_tokens, top_p=top_p)
        generation_end_time = time.time()  # End LLaMA generation timing
    except Exception as e:
        print("⚠️ LLaMA Model Error:", str(e))
        return "⚠️ Model generation failed.", full_context, retrieval_latency, reranker_latency

    return response, full_context, retrieval_latency, reranker_latency
'''

#use this function if you want to remove the reranking layer
def chatbot_response(user_input, rag_enabled=False, threshold=None, temperature=None, max_tokens=None, top_p=None):
    """Uses RAG pipeline without reranking before passing context to LLaMA."""
    
    start_time = time.time()  # Start measuring total latency

    if not isinstance(user_input, str):
        print("⚠️ ERROR: user_input must be a string. Received:", type(user_input))
        return "⚠️ Invalid input format.", None, None, None  # Return placeholders

    print("\n🔍 Query before embedding:", repr(user_input))

    # ✅ Use default model parameters if not provided
    temperature = temperature if temperature is not None else MODEL_PARAMS["temperature"]
    max_tokens = max_tokens if max_tokens is not None else MODEL_PARAMS["max_tokens"]
    top_p = top_p if top_p is not None else MODEL_PARAMS["top_p"]

    if rag_enabled:
        try:
            retrieval_start_time = time.time()  # Start retrieval timing
            retrieved_docs = retriever.invoke(user_input)  # ✅ Retrieve documents
            retrieval_end_time = time.time()  # End retrieval timing
        except Exception as e:
            print("⚠️ FAISS Retrieval Error:", str(e))
            return "⚠️ Retrieval failed.", None, None, None

        if not retrieved_docs:
            return "⚠️ No relevant information found in the knowledge base.", None, retrieval_end_time - retrieval_start_time, None

        retrieval_latency = retrieval_end_time - retrieval_start_time

        # ❌ **Remove reranking** (previously using Cross-Encoder)
        filtered_docs = retrieved_docs  # ✅ Use all retrieved docs without reranking
        reranker_latency = None  # ✅ Set reranker time to None

        print("\n📜 DEBUG: Retrieved Documents Without Reranking:")
        for doc in filtered_docs:
            print(f"{doc.page_content[:200]}...\n")

        # ✅ Ensure the context fits within LLaMA's context limit
        full_context = truncate_context_to_fit(
            filtered_docs,
            user_input,
            max_tokens=MODEL_PARAMS["n_ctx"] - 200,  # Apply 200-token safety buffer
            avg_chars_per_token=3.5
        )

        if not full_context.strip():
            full_context = "No relevant documents found."
    else:
        full_context = "No context provided."
        retrieval_latency = None
        reranker_latency = None

    final_prompt = f"""
    You are an AI assistant. Use the provided context to answer the question.

    Context:
    {full_context}

    Question:
    {user_input}

    Now give me your response to the question based on the context provided:
    """

    print("\n📜 DEBUG: Final Prompt Sent to LLaMA:\n", final_prompt, "...")

    try:
        generation_start_time = time.time()  # Start LLaMA generation timing
        response = llm.invoke(final_prompt, temperature=temperature, max_tokens=max_tokens, top_p=top_p)
        generation_end_time = time.time()  # End LLaMA generation timing
    except Exception as e:
        print("⚠️ LLaMA Model Error:", str(e))
        return "⚠️ Model generation failed.", full_context, retrieval_latency, reranker_latency

    return response, full_context, retrieval_latency, reranker_latency  # ✅ Reranker latency will now be `None`
'''

if __name__ == "__main__":
    while True:
        user_input = input("\n🔍 Enter query (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        response = chatbot_response(user_input, rag_enabled=rag_enabled, temperature=temp, max_tokens=max_tokens, top_p=top_p)
        print("\n💬 Chatbot Response:\n", response)

