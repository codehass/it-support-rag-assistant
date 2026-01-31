import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.Doduments import Document

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
data_path = "data/data.pdf"


def load_and_split_documents(data_path: str) -> list[Document]:
    """
    load_and_split_documents - Loads and splits documents from the given data path

    :param data_path: Data path to PDF file
    :type data_path: str
    :return: List of split Document objects
    :rtype: list
    """
    loader = PyPDFLoader(data_path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(docs)


def save_splits_to_chroma(
    splits: list[Document], chroma_db_path: str = "./chroma_db"
) -> None:
    """
    Docstring for save_splits_to_chroma

    :param splits: Description
    :type splits: list[Document]
    :param chroma_db_path: Description
    :type chroma_db_path: str
    """
    embedding_function = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={"token": HF_TOKEN},
    )
    print("Creating vector database... this may take a moment.")
    Chroma.from_documents(
        documents=splits, embedding=embedding_function, persist_directory=chroma_db_path
    )
    print(f"Success! {len(splits)} chunks saved.")


splits = load_and_split_documents(data_path)
save_splits_to_chroma(splits)
