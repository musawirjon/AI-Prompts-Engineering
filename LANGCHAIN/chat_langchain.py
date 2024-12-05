import os
from dotenv import load_dotenv
import json
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA 
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss
import numpy as np

class ChatLangchain:
    def __init__(self):
        # Load environment variables from a `.env` file (optional)
        load_dotenv()

        self.name = "Scrapping RAG"
        self.endpoint = os.getenv("OPENAI_API_URL")
        self.api_key = os.getenv("OPENAI_API_KEY").strip()
        self.model_name = os.getenv("MODEL_NAME")
        self.version = os.getenv("VERSION")

        # For debugging, print loaded environment variables (optional)
        # print('===============================', self.api_key, '===============================')

        # Validate required environment variables (recommended)
        if not all([self.endpoint, self.api_key, self.model_name, self.version]):
            raise ValueError("Missing required environment variables: OPENAI_API_URL, OPENAI_API_KEY, MODEL_NAME, VERSION")

        # Construct the full URL using f-strings for clarity
        self.api_url = f"{self.endpoint}/openai/deployments/{self.model_name}/chat/completions?api-version={self.version}"

        # Print the constructed API URL for informational purposes
        print(f"Constructed API URL: {self.api_url}")
 
    def initialize_langchain(self):
        
        def load_faiss_index(self, index_path="faiss_index.index"):
            return faiss.read_index(index_path)
        
        index = load_faiss_index

        def index_to_docstore_id(self,index_id):
            # Implement your logic to map index IDs to document IDs
            return str(index_id)
        
        docstore = InMemoryDocstore({})

        embeddings = AzureOpenAIEmbeddings(
            openai_api_key=self.api_key,
            deployment="cubeone-embedding-deployment",
            openai_api_version=self.version,
            azure_endpoint=self.endpoint,
            openai_api_type="azure"
        )
        # Create FAISS vector store
        vectorstore = FAISS(
            index=index,
            embedding_function=embeddings,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id
        )

        # Create RetrievalQA chain with AzureOpenAI embeddings and FAISS retriever
        qa_chain = RetrievalQA.from_chain_type(
            llm=embeddings,
            retriever=vectorstore.as_retriever()
        )

        return qa_chain

    def load_embeddings_from_json(self, filename="embeddings.json"):
        with open(filename, 'r') as f:
            data = json.load(f)
        return np.array(data["embeddings"]), data["texts"]