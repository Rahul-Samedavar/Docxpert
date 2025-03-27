import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from openai import OpenAI
import os


from PyPDF2 import PdfReader
from docx import Document

import keys

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def init_chroma(persist_dir: str = "./chroma_db"):
    client = chromadb.Client(Settings(persist_directory=persist_dir))
    return client


def create_vectorstore(client, collection_name: str, documents: list, embeddings_model="text-embedding-ada-002"):
    collection = client.create_collection(name=collection_name)
    
    embedding_model = OpenAIEmbeddings(model_name=embeddings_model)
    texts = [doc["content"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    ids = [doc["id"] for doc in documents]

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )
    
    vectorstore = Chroma(client=client, collection_name=collection_name, embedding_function=embedding_model)
    return vectorstore


def load_documents(file_paths):
    documents = []
    for idx, file_path in enumerate(file_paths):
        content = ""
        ext = file_path.split(".")[-1].lower()

        try:
            if ext == "txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

            elif ext == "pdf":
                reader = PdfReader(file_path)
                content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

            elif ext == "docx":
                doc = Document(file_path)
                content = "\n".join([para.text for para in doc.paragraphs])

            else:
                print(f"Unsupported file format: {file_path}")
                continue

            documents.append({
                "id": f"doc_{idx}",
                "content": content,
                "metadata": {"source": file_path}
            })

        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return documents


def save_vectorstore(vectorstore, persist_dir="./chroma_db"):
    """
    Save ChromaDB vectorstore to disk.
    """
    vectorstore.persist(persist_dir)


def load_vectorstore(client, collection_name):
    """
    Load an existing ChromaDB vectorstore.
    
    Args:
        client: ChromaDB client instance.
        collection_name: Name of the collection.
    
    Returns:
        Chroma vectorstore object.
    """
    embedding_model = OpenAIEmbeddings(model_name="text-embedding-ada-002")
    vectorstore = Chroma(client=client, collection_name=collection_name, embedding_function=embedding_model)
    return vectorstore
