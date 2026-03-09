# Project: Rahul-Samedavar/Docxpert

## Overview

**Docxpert** is a comprehensive tool for working with RAG (Relevance, Accuracy, and Granularity) databases. It provides a Flask application for ingesting and querying RAG databases through the `app.py` module, as well as a set of utility functions in `util.py` for tasks such as document loading, text splitting, Chroma saving, and RAG model querying. Additionally, Docxpert offers functionality for generating context-aware queries and summarizing PDFs, making it a powerful solution for document analysis and management.

## Project Structure

The project is organized into several key directories, each with its own role:

* **`app.py`**: This module implements a Flask application for ingesting and querying RAG databases.
* **`util.py`**: This module provides utility functions for loading documents, splitting text, saving to Chroma, and querying the RAG model. It also includes functions for generating context-aware queries and summarizing PDFs.
* **`static`**: This directory is used to store static assets for the RAG application, including files that are not dynamically generated and are served directly by the web server.
* **`templates`**: This directory contains HTML, CSS, and other static files used to define the structure and layout of the RAG application's user interface.

## Key Features

Based on the provided context, the key features of Docxpert include:

* **Multi-File Support**: Upload and query PDF, Word (.docx), and Text (.txt) files.
* **Context-Aware Chat**: Conversations maintain flow with memory of previous queries.
* **Document Preview with Navigation**: Embedded viewer with clickable source references for fast navigation.
* **Temporary Session Memory**: Sessions persist until server restarts, allowing page reloads without data loss.
* **Exportable Chat History**: Save your entire chat as a PDF file with one click.
* **Interact with Multiple Files**: Seamlessly query multiple files at once—no need to clear history.
* **Clear Chat Option**: Easily reset conversation context.
* **Text-to-Speech Responses**: Click to listen to responses—great for accessibility and hands-free use.
* **Document Summarization to PDF**: Summarize uploaded documents with one click and export summaries as PDFs.

## Tech Stack

* **LLM**: OpenAI GPT
* **Framework**: LangChain
* **Backend**: Flask (Python)
* **Vector Store**: ChromaDB
* **UI**: HTML, CSS, JavaScript
* **File Handling**: PyMuPDF, pdfkit, python-docx, docx2txt

## Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Rahul-Samedavar/Docxpert.git
cd Docxpert
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows
```

create a file named keys.py and add you OpenAI key as
```python 
import os

os.environ['OPENAI_API_KEY'] = "Your OpenAI API key"
os.environ['OPENAI_MODEL'] = "gpt-3.5-turbo"
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the App
```bash
python app.py
```
Then open:
```
http://127.0.0.1:5000
```

## License

This project is licensed under the [**MIT License**](LICENSE).