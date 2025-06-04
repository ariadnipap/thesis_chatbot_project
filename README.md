# Thesis Chatbot Project

This project is a **chatbot assistant for engineering teams**, developed as part of a thesis in collaboration with Intracom Telecom. It uses a custom RAG (Retrieval-Augmented Generation) pipeline to answer technical queries based on internal documentation and support data.

---

## Getting Started

### Prerequisites

- Python 3.10+
- A working virtual environment (recommended)
- Required Python packages (see below)

### Install Dependencies

From the root directory:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> Note: The `venv/` folder is excluded from version control. You'll need to recreate it.

---

## How It Works

The chatbot is powered by:

- A **RAG architecture** using embeddings
- An open-source **LLM** (e.g. LLaMA 3)
- Documents and historical service requests as knowledge sources

It provides engineers with accurate, context-aware answers when installing, configuring, or troubleshooting the BigData platform.

---

## Run the Chatbot

To launch the chatbot UI:

```bash
python3 ui/chatbot_ui.py
```

---

## Author

**Ariadni Papanikolaou**  
ECE NTUA | Thesis in collaboration with Intracom Telecom

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.
