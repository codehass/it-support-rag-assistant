import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


embedding_function = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)


system_prompt = (
    "You are an IT Support Assistant. Use the following context to answer the question. "
    "If you don't know the answer, say you don't know. Keep it brief.\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

retriever = db.as_retriever()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


user_input = input("\nWhat is your IT support question? ")
if user_input:
    response = rag_chain.invoke(user_input)
    print("\n--- Answer ---")
    print(response)
