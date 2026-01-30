import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class ITSmartAssistant:
    def __init__(self):
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )
        self.db = Chroma(
            persist_directory="./chroma_db", embedding_function=self.embedding_function
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7,
        )

        self.chain = self._build_chain()

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def _build_chain(self):
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

        retriever = self.db.as_retriever()

        return (
            {"context": retriever | self._format_docs, "input": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, question: str):
        return {"query": question, "answer": self.chain.invoke(question)}


# query = "How to reset my IT support password?"
# rag_system = ITSmartAssistant()
# answer = rag_system.ask(query)
# print(answer)
