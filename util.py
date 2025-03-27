from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain.embeddings import OpenAIEmbeddings 
from langchain.schema import Document 
from langchain.vectorstores.chroma import Chroma 
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import keys
import shutil
from docx import Document

CHROMA_Folder = "chroma"

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


def save_to_chroma(chunks: list[Document], file_path):
    """Save chunks to ChromaDB"""
    CHROMA_PATH = os.path.join(CHROMA_Folder, file_path)
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(),
        persist_directory=CHROMA_PATH
    )


def ingest(file_path, db_name):
    """Ingest file into vector store"""
    documents = load_document(file_path)
    chunks = split_text(documents)
    save_to_chroma(chunks, db_name)


def search(query, db_path):
    """Search for relevant content"""
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=os.path.join(CHROMA_Folder, db_path), embedding_function=embedding_function)
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


def query_rag(query_text, db_path):
    """Query using RAG pipeline with ChromaDB"""
    results = search(query_text, db_path)

    if len(results) == 0 or results[0][1] < 0.7:
        return "No relevant information found.", []

    context_text = "\n\n - -\n\n".join([doc.page_content for doc, _ in results])
    sources_with_pages = extract_page_numbers(results)

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = ChatOpenAI()
    response_text = model.predict(prompt)

    return response_text, sources_with_pages
