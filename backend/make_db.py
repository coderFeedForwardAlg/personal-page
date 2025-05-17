# from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai 
from dotenv import load_dotenv
import os
import shutil




# Load environment variables from .env file
load_dotenv()

# Check if OPENAI_API_KEY is set
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file or environment.")

CHROMA_PATH = 'chroma'

DATA_PATH = 'data/about'

def main():
    generate_data_store()

def generate_data_store():
    docs = load_documents()
    chunks = split_text(docs)
    save_to_chroma(chunks)


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    docs = loader.load()
    return docs


def split_text(docs: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 300,
        chunk_overlap = 100,
        length_function = len,
        add_start_index = True
    )
    chunks = text_splitter.split_documents(docs)

    return chunks


def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    embedding_function = OpenAIEmbeddings(openai_api_key=api_key)
    db = Chroma.from_documents(
        chunks, embedding_function, persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


if __name__ == "__main__":
    main() 