import sys
import os
import gradio as gr
import webbrowser
import json

# Add path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.chatbot_english import chatbot_response

CONFIG_PATH = "/home/ariadnipap/thesis_chatbot_project/scripts/config.json"

def update_config(top_k, top_p, chunking_type):
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    config["model_parameters"]["top_k"] = int(top_k)
    config["model_parameters"]["top_p"] = float(top_p)

    chunk_key_map = {
        "No Chunking (0)": "faiss_index_new",
        "Chunking 1000-100": "faiss_index_chunked_1000_100",
        "Chunking 2000-200": "faiss_index_chunked_2000_200"
    }

    faiss_dir = f"data/{chunk_key_map[chunking_type]}/"
    config["paths"]["faiss_index"] = faiss_dir

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def chat_interface(user_input, history=[], rag_enabled=False, top_k=50, top_p=0.88,
                   chunking_type="No Chunking (0)", use_reranker=True, threshold=-8.0):
    if not history:
        history = []

    update_config(top_k, top_p, chunking_type)

    history.append((user_input, ""))
    yield history, ""

    bot_response, *_ = chatbot_response(
        user_input,
        rag_enabled=rag_enabled,
        threshold=threshold,
        top_p=top_p
    )

    if not isinstance(bot_response, str):
        bot_response = str(bot_response)

    history[-1] = (user_input, bot_response)
    yield history, ""

def open_new_chat():
    webbrowser.open("http://127.0.0.1:7860")

# UI Layout
with gr.Blocks(css="custom-css") as chatbot_ui:
    with gr.Row():
        with gr.Column(scale=1, min_width=250):
            gr.Markdown("### **Chatbot Settings**")
            new_thread_button = gr.Button("New Thread")
            new_thread_button.click(open_new_chat)

            rag_toggle = gr.Checkbox(label="Enable RAG", value=False)

            top_k_dropdown = gr.Dropdown(choices=[10, 25, 50], value=50, label="Top K")
            top_p_dropdown = gr.Dropdown(choices=[0.55, 0.7, 0.88], value=0.88, label="Top P")

            chunking_dropdown = gr.Dropdown(
                choices=["No Chunking (0)", "Chunking 1000-100", "Chunking 2000-200"],
                value="No Chunking (0)",
                label="Chunking Strategy"
            )

            use_reranker_checkbox = gr.Checkbox(label="Use Reranker", value=True)
            threshold_slider = gr.Slider(minimum=-10.0, maximum=2.0, value=-8.0, step=0.1, label="Reranker Threshold")

        with gr.Column(scale=3):
            gr.Markdown("## **Chatbot Interface**")
            chatbot = gr.Chatbot(label="Chat History", height=500, elem_id="chat_display")
            user_input = gr.Textbox(placeholder="Type your message here...", label="Your Query")

            with gr.Row():
                submit_button = gr.Button("Send")
                clear_button = gr.Button("Clear Chat")

            submit_button.click(
                chat_interface,
                inputs=[
                    user_input, chatbot, rag_toggle,
                    top_k_dropdown, top_p_dropdown,
                    chunking_dropdown,
                    use_reranker_checkbox, threshold_slider
                ],
                outputs=[chatbot, user_input]
            )

            clear_button.click(lambda: ([], ""), inputs=None, outputs=[chatbot, user_input])

    gr.Markdown(
        """
        ---
        **This chatbot was developed by Ariadni Papanikolaou as part of her undergraduate thesis in Electrical and Computer Engineering at NTUA, in collaboration with Intracom Telecom Greece.**  
        The project focuses on Retrieval-Augmented Generation (RAG) for engineering support and integrates open-source LLMs and document retrieval systems.
        """,
        elem_id="footer"
    )

# Launch app
if __name__ == "__main__":
    chatbot_ui.launch(server_name="0.0.0.0", server_port=7860)


'''
# use this code if you want streaming, however, note that it messes with the answers
import sys
import os
import gradio as gr
import webbrowser
import json

# Add path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.chatbot_english import chatbot_response_stream
from scripts.chatbot_english import chatbot_response

CONFIG_PATH = "/home/ariadnipap/thesis_chatbot_project/scripts/config.json"

def update_config(top_k, top_p, chunking_type, embedding_model):
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    config["model_parameters"]["top_k"] = int(top_k)
    config["model_parameters"]["top_p"] = float(top_p)

    chunk_key_map = {
        "No Chunking (0)": "faiss_index",
        "Chunking 500-100": "faiss_index_chunked_500_100",
        "Chunking 1000-200": "faiss_index_chunked_1000_200"
    }

    chunk_key = chunk_key_map[chunking_type]
    emb_suffix = "_mpnet" if embedding_model == "MPNet" else ""

    faiss_dir = f"data/{chunk_key}{emb_suffix}/"
    config["paths"]["faiss_index"] = faiss_dir

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def chat_interface(user_input, history=[], rag_enabled=False, top_k=50, top_p=0.88,
                   chunking_type="No Chunking (0)", embedding_model="MiniLM",
                   use_reranker=True, threshold=-8.0):
    if not history:
        history = []

    update_config(top_k, top_p, chunking_type, embedding_model)
    history.append((user_input, ""))
    yield history, ""

    for bot_response, _, _, _ in chatbot_response_stream(
        user_input,
        rag_enabled=rag_enabled,
        top_k=top_k,
        top_p=top_p,
        use_reranker=use_reranker,
        threshold=threshold
    ):
        if not isinstance(bot_response, str):
            bot_response = str(bot_response)

        history[-1] = (user_input, bot_response)
        yield history, ""

    history[-1] = (user_input, bot_response)
    yield history, ""

def open_new_chat():
    webbrowser.open("http://127.0.0.1:7860")

# UI Layout
with gr.Blocks(css="custom-css") as chatbot_ui:
    with gr.Row():
        with gr.Column(scale=1, min_width=250):
            gr.Markdown("### **Chatbot Settings**")
            new_thread_button = gr.Button("New Thread")
            new_thread_button.click(open_new_chat)

            rag_toggle = gr.Checkbox(label="Enable RAG", value=False)

            top_k_dropdown = gr.Dropdown(choices=[10, 25, 50], value=50, label="Top K")
            top_p_dropdown = gr.Dropdown(choices=[0.55, 0.7, 0.88], value=0.88, label="Top P")

            chunking_dropdown = gr.Dropdown(
                choices=["No Chunking (0)", "Chunking 500-100", "Chunking 1000-200"],
                value="No Chunking (0)",
                label="Chunking Strategy"
            )

            embedding_dropdown = gr.Dropdown(
                choices=["MiniLM", "MPNet"],
                value="MiniLM",
                label="Embedding Model"
            )

            use_reranker_checkbox = gr.Checkbox(label="Use Reranker", value=True)
            threshold_slider = gr.Slider(minimum=-10.0, maximum=2.0, value=-8.0, step=0.1, label="Reranker Threshold")

        with gr.Column(scale=3):
            gr.Markdown("## **Chatbot Interface**")
            chatbot = gr.Chatbot(label="Chat History", height=500, elem_id="chat_display")
            user_input = gr.Textbox(placeholder="Type your message here...", label="Your Query")

            with gr.Row():
                submit_button = gr.Button("Send")
                clear_button = gr.Button("Clear Chat")

            submit_button.click(
                chat_interface,
                inputs=[
                    user_input, chatbot, rag_toggle,
                    top_k_dropdown, top_p_dropdown,
                    chunking_dropdown, embedding_dropdown,
                    use_reranker_checkbox, threshold_slider
                ],
                outputs=[chatbot, user_input]
            )

            clear_button.click(lambda: ([], ""), inputs=None, outputs=[chatbot, user_input])

    # Footer section
    gr.Markdown(
        """
        ---
        **This chatbot was developed by Ariadni Papanikolaou as part of her undergraduate thesis in Electrical and Computer Engineering at NTUA, in collaboration with Intracom Telecom Greece.**  
        The project focuses on Retrieval-Augmented Generation (RAG) for engineering support and integrates open-source LLMs and document retrieval systems.
        """,
        elem_id="footer"
    )

# Launch app
if __name__ == "__main__":
    chatbot_ui.launch(server_name="0.0.0.0", server_port=7860)
'''