from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import tempfile
import shutil
import atexit
import keys

TEMP_BASE_FOLDER = tempfile.mkdtemp()



def cleanup():
    shutil.rmtree(TEMP_BASE_FOLDER)
    shutil.rmtree("uploads")

atexit.register(cleanup)

docs_count = 0
def get_unique_filename():
    global docs_count
    docs_count += 1
    return f"f_{docs_count}.pdf"


def load_document(file_path):
    if file_path.endswith(".pdf"):
        return PyMuPDFLoader(file_path=file_path).load()
    elif file_path.endswith(".txt"):
        return TextLoader(file_path).load()
    elif file_path.endswith(".docx"):
        return Docx2txtLoader(file_path).load()
    else:
        raise ValueError("Unsupported file format")


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150, length_function=len, add_start_index=True)
    chunks = text_splitter.split_documents(documents)
    return chunks


def save_to_chroma(chunks: list[Document], db_name):
    CHROMA_PATH = os.path.join(TEMP_BASE_FOLDER, db_name)

    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(),
        persist_directory=CHROMA_PATH
    )
    return db


def ingest(file_path, db_name):
    documents = load_document(file_path)
    chunks = split_text(documents)
    save_to_chroma(chunks, db_name)


def search(query, db_path):
    db_dir = os.path.join(TEMP_BASE_FOLDER, db_path)
    embedding_function = OpenAIEmbeddings()
    
    if not os.path.exists(db_dir):
        print("lol:", db_dir)
        return []

    db = Chroma(persist_directory=db_dir, embedding_function=embedding_function)
    return db.similarity_search_with_relevance_scores(query, k=3)


def extract_page_numbers(results):
    sources_with_pages = []
    for doc, _ in results:
        page_number = doc.metadata.get("page", "N/A")
        sources_with_pages.append(f"p.{page_number+1}")
    return sources_with_pages


PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}
 - -
Answer the question based on the above context: {question}
"""


def query_rag(query_text, db_name):
    results = search(query_text, db_name)

    if len(results) == 0 or results[0][1] < 0.4:
        return "No relevant information found.", []

    context_text = "\n\n - -\n\n".join([doc.page_content for doc, _ in results])
    sources_with_pages = extract_page_numbers(results)

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = ChatOpenAI()
    response_text = model.predict(prompt)

    return response_text, sources_with_pages

from langchain_core.prompts import PromptTemplate

CONT_AWARE_QUERY_TEMPLATE = """
You are an RAG prompt generator. 
Read the chat history and users query and modify the user query to include relevant context from the chat history.
Your response should be as small as possible but shouldnt have any missing context.

You are a RAG Prompt Generator.
You are given a Chat History and a User Query. Your task is to convert User Query into Cntext Aware Query by filling out references from previous history.
This Context Aware Query should be understandable without chat history.
Keep it simple, short and similar to user query, remove any stopping word.

Example:
    Chat History:
    User: Who all were the part of this project?
    Bot: John Doe and Jane Foster.
    
    User Query: Tell me more about them?

    Context Aware Query: about John Doe and Jane Foster
    

Chat History:
{history}

User Query:
{query}

Context Aware Query:
"""

def context_aware_query(history, query):
    prompt_template = PromptTemplate.from_template(CONT_AWARE_QUERY_TEMPLATE)
    prompt = prompt_template.format(history=history, query=query)

    model = ChatOpenAI()
    cont_awar_query = model.predict(prompt)

    return cont_awar_query
