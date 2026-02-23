# PDF Chunking + Embedding (LOCAL FAISS)

import os
import glob
import logging
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("indexer")


def index_docs():
    """
    Reads PDFs from backend/data,
    chunks them,
    embeds them using HuggingFace,
    and stores locally in FAISS.
    """

    # Locate data folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir, "../data")
    
#locate both folders using glob 
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
#SAFETY if no pdf found
    if not pdf_files:
        logger.warning("No PDF files found in data folder.")
        return

    documents = []

    # Load PDFs
    for pdf in pdf_files:
        logger.info(f"Loading: {pdf}")
        loader = PyPDFLoader(pdf)
        documents.extend(loader.load())

    logger.info(f"Total pages loaded: {len(documents)}")

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)
    logger.info(f"Total chunks created: {len(chunks)}")

    # Add metadata 
    for chunk in chunks:
        chunk.metadata["source"] = chunk.metadata.get("source", "unknown")

    # Embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Create FAISS vector store
    vector_store = FAISS.from_documents(chunks, embeddings)

    # Save locally
    save_path = os.path.join(data_folder, "faiss_index")
    os.makedirs(save_path, exist_ok=True)
    vector_store.save_local(save_path)

    logger.info("FAISS index created and saved successfully!")


if __name__ == "__main__":
    index_docs()