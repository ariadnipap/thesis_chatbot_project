
import sys
import os
import gradio as gr
import webbrowser
import time  # Added for the typing effect

# Ensure the scripts directory is in Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.chatbot_english import chatbot_response  # change to chatbot_greek for multilingual
import time

def chat_interface(user_input, history=[], rag_enabled=False, temp=0.7, max_tokens=8192, top_p=0.95, prompt_template=""):
    if not history:
        history = []

    if prompt_template:
        user_input = prompt_template.replace("{prompt}", user_input)

    # Append user message properly (Avoiding empty message issue)
    history.append((user_input, ""))  
    yield history, ""  # Clear input box immediately

    # Call chatbot and unpack response
    bot_response, full_context, retrieval_latency, reranker_latency = chatbot_response(
        user_input, rag_enabled=rag_enabled, temperature=temp, max_tokens=max_tokens, top_p=top_p
    )

    # Ensure bot_response is a string
    if not isinstance(bot_response, str):
        bot_response = str(bot_response)

    displayed_response = ""
    for char in bot_response:
        displayed_response += char  # ✅ Now bot_response is correctly treated as a string
        time.sleep(0.02)  
        history[-1] = (user_input, displayed_response)  
        yield history, ""

    # Ensure the final bot response is saved
    history[-1] = (user_input, bot_response)
    yield history, ""



def open_new_chat():
    """Opens a new instance of the chatbot UI in a new browser window."""
    webbrowser.open("http://127.0.0.1:7860")  


# UI Layout
with gr.Blocks(css="custom-css") as chatbot_ui:
    with gr.Row():
        with gr.Column(scale=1, min_width=250):
            gr.Markdown("### **Menu**")
            new_thread_button = gr.Button("New Thread")
            new_thread_button.click(open_new_chat)

            gr.Markdown("### **Model**")
            model_name = gr.Markdown("LLaMA 3.3 70B Instruct Q4")  # Fixed Model Name
            rag_toggle = gr.Checkbox(label="Enable RAG", value=False)  # Toggle for RAG
            
            gr.Markdown("### **Inference Settings**")
            temp_slider = gr.Slider(0, 2, value=0.7, label="Temperature")
            top_p_slider = gr.Slider(0, 1, value=0.95, label="Top P")
            max_tokens_slider = gr.Slider(100, 8192, value=8192, label="Max Tokens")
            freq_penalty_slider = gr.Slider(0, 1, value=0, label="Frequency Penalty")
            presence_penalty_slider = gr.Slider(0, 1, value=0, label="Presence Penalty")
            stop_words_box = gr.Textbox(label="Stop Words (comma-separated)", placeholder="e.g., <end_of_text>,<eom_id>")

            gr.Markdown("### **Model Settings**")
            prompt_template_box = gr.Textbox(label="Prompt Template", placeholder="Define a prompt format...")

            gr.Markdown("### **Engine Settings**")
            context_length_slider = gr.Slider(128, 131072, value=8192, label="Context Length")
            gpu_layers_slider = gr.Slider(1, 100, value=33, label="Number of GPU Layers")

        with gr.Column(scale=3):
            gr.Markdown("## **Chatbot Interface**")
            chatbot = gr.Chatbot(label="Chat History", height=500, elem_id="chat_display")  # Added CSS styling
            user_input = gr.Textbox(placeholder="Type your message here...", label="Your Query")
            
            with gr.Row():
                submit_button = gr.Button("Send")
                clear_button = gr.Button("Clear Chat")
            
            submit_button.click(
                chat_interface,
                inputs=[user_input, chatbot, rag_toggle, temp_slider, max_tokens_slider, top_p_slider, prompt_template_box],
                outputs=[chatbot, user_input]  # Clears input after sending
            )
            
            clear_button.click(lambda: ([], ""), inputs=None, outputs=[chatbot, user_input])

# Run UI
if __name__ == "__main__":
    chatbot_ui.launch(server_name="0.0.0.0", server_port=7860)

