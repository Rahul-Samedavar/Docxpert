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

# Create a temporary base folder for Chroma
TEMP_BASE_FOLDER = tempfile.mkdtemp()



# Ensure the temporary base folder is deleted on exit
def cleanup():
    shutil.rmtree(TEMP_BASE_FOLDER)

atexit.register(cleanup)

docs_count = 0
def get_unique_filename():
    global docs_count
    docs_count += 1
    return f"doc_{docs_count}"


def load_document(file_path):
    """Load documents based on file type"""
    if file_path.endswith(".pdf"):
        return PyMuPDFLoader(file_path=file_path).load()
    elif file_path.endswith(".txt"):
        return TextLoader(file_path).load()
    elif file_path.endswith(".docx"):
        return Docx2txtLoader(file_path).load()
    else:
        raise ValueError("Unsupported file format")


def split_text(documents: list[Document]):
    """Split documents into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100, length_function=len, add_start_index=True)
    chunks = text_splitter.split_documents(documents)
    return chunks


def save_to_chroma(chunks: list[Document], db_name):
    """Save chunks to ChromaDB in a subdirectory"""
    CHROMA_PATH = os.path.join(TEMP_BASE_FOLDER, db_name)

    # Remove previous folder if exists
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(),
        persist_directory=CHROMA_PATH
    )
    return db


def ingest(file_path):
    db_name = get_unique_filename()
    """Ingest file into vector store with subdirectories"""
    documents = load_document(file_path)
    chunks = split_text(documents)
    save_to_chroma(chunks, db_name)
    return db_name


def search(query, db_path):
    """Search for relevant content"""
    db_dir = os.path.join(TEMP_BASE_FOLDER, db_path)
    embedding_function = OpenAIEmbeddings()
    
    if not os.path.exists(db_dir):
        return []

    db = Chroma(persist_directory=db_dir, embedding_function=embedding_function)
    return db.similarity_search_with_relevance_scores(query, k=3)


def extract_page_numbers(results):
    """Extract page numbers from document metadata"""
    sources_with_pages = []
    for doc, _ in results:
        page_number = doc.metadata.get("page", "N/A")
        sources_with_pages.append(f"p.{page_number}")
    return sources_with_pages


PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}
 - -
Answer the question based on the above context: {question}
"""


def query_rag(query_text, db_name):
    """Query using RAG pipeline with ChromaDB"""
    results = search(query_text, db_name)

    if len(results) == 0 or results[0][1] < 0.7:
        return "No relevant information found.", []

    context_text = "\n\n - -\n\n".join([doc.page_content for doc, _ in results])
    sources_with_pages = extract_page_numbers(results)

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = ChatOpenAI()
    response_text = model.predict(prompt)

    return response_text, sources_with_pages

from langchain_core.prompts import PromptTemplate

# Template for generating simplified RAG query
SIMPLE_QUERY_PROMPT = """
You are an RAG prompt generator. Your Task is to read the conversation history and a user query and respond with a context aware query. Keep it short and simple and avoid stopping words.

Chat History:
{history}

Current Query:
{query}

Context Aware Query:
"""

def context_aware_query(history, query):
    prompt_template = PromptTemplate.from_template(SIMPLE_QUERY_PROMPT)
    prompt = prompt_template.format(history=history, query=query)

    model = ChatOpenAI()
    simplified_query = model.predict(prompt)

    return simplified_query
