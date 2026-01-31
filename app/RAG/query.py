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
HF_TOKEN = os.getenv("HF_TOKEN")


class ITSmartAssistant:
    def __init__(self):
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"token": HF_TOKEN},
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
            '- If the answer is not in the context, respond: "I don’t know." '
            "- Provide step-by-step instructions if applicable. "
            "- Include citations for any information taken from the context in the format: [source, page]. "
            "- Keep answers clear and concise.\n\n"
            "Context:\n{context}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

        return prompt | self.llm | StrOutputParser()

    def ask(self, question: str):
        retriever = self.db.as_retriever()
        docs = retriever.invoke(question)

        context = self._format_docs(docs)
        answer = self.chain.invoke(
            {
                "context": context,
                "input": question,
            }
        )

        chunks = [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page"),
            }
            for doc in docs
        ]

        return {
            "query": question,
            "answer": answer,
            "chunks": chunks,
        }


# query = "How to reset my IT support password?"
# rag_system = ITSmartAssistant()
# answer = rag_system.ask(query)
# print(answer)
