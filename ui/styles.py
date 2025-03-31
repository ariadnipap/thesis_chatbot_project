custom_css = """
    /* Chatbot Styling */
    .gradio-container { background-color: #f8f9fa; font-family: 'Arial', sans-serif; }

    /* Chat messages */
    .gr-chatbot { 
        background-color: #ffffff; 
        border-radius: 10px; 
        padding: 15px; 
        overflow-y: auto;
        max-height: 500px;
    }

    /* User Messages */
    .gr-chatbot .user { 
        text-align: right;
        background: #dff9fb;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
        color: #222;
        display: inline-block;
        max-width: 75%;
    }

    /* Bot Messages */
    .gr-chatbot .bot { 
        text-align: left;
        font-weight: bold;
        color: #222222;
        border-left: 4px solid #007bff;
        padding-left: 10px;
        background: #e8f0fe;
        padding: 10px;
        border-radius: 10px;
        display: inline-block;
        max-width: 75%;
    }
"""
