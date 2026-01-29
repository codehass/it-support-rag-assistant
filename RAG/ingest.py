import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# 1. Load & Split
loader = PyPDFLoader("data/data.pdf")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# 2. Setup Embeddings
embedding_function = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

# 3. Create/Save Vector Store
print("Creating vector database... this may take a moment.")
db = Chroma.from_documents(
    documents=splits, embedding=embedding_function, persist_directory="./chroma_db"
)
print(f"Success! {len(splits)} chunks saved to ./chroma_db")
