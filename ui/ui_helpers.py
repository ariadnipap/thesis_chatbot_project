import gradio as gr

def custom_markdown(text):
    """Returns styled markdown text for UI components."""
    return gr.Markdown(f"**{text}**")

def custom_button(label, color="primary"):
    """Creates a styled button for Gradio UI."""
    return gr.Button(label, elem_id=color)
