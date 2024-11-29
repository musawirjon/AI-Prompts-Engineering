from langchain.chains import RetrievalQA
from langchain.llms import AzureOpenAI
from langchain.vectorstores import FAISS
from langchain.vectorstores.faiss import FAISS
from langchain.prompts import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from openai import AzureOpenAI
import os

class ChatLangchain():
    def __init__(self):
        self.name = "Scrapping RAG"
        self.endpoint = os.getenv("OPENAI_API_URL")
        self.API_KEY = os.getenv("OPENAI_API_KEY")
        self.MODEL_NAME = os.getenv("MODEL_NAME")
        self.VERSION = os.getenv("VERSION")
        self.llm = AzureOpenAI(azure_endpoint=self.endpoint,api_version=self.VERSION,api_key=self.API_KEY)

    # Initialize the LangChain retrieval system
    def initialize_langchain(self,index):
        # Use OpenAIEmbeddings to match the stored data with queries
        embeddings = OpenAIEmbeddings()
        
        # Initialize the FAISS vector store
        vectorstore = FAISS(index, embeddings)

        # Initialize QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm, 
            retriever=vectorstore.as_retriever()
        )

        return qa_chain
