import os
from dotenv import load_dotenv
import json
from langchain_openai import AzureOpenAIEmbeddings, AzureOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
import chromadb
from chromadb.config import Settings
from datetime import datetime
from typing import List, Optional

class ChatLangchain:
    def __init__(self):
        # Load environment variables from a `.env` file
        load_dotenv()

        self.name = "Chat Langchain"
        self.endpoint = os.getenv("OPENAI_API_URL")
        self.api_key = os.getenv("OPENAI_API_KEY").strip()
        self.model_name = os.getenv("MODEL_NAME")
        self.version = os.getenv("VERSION")

        # Validate required environment variables
        if not all([self.endpoint, self.api_key, self.model_name, self.version]):
            raise ValueError("Missing required environment variables")

        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_version=self.version,
            api_key=self.api_key
        )

        # Initialize ChromaDB client with persistent storage
        self.persist_directory = "chroma_storage"
        self.embeddings = self._create_embeddings()
        self.vectorstore = None

    def _create_embeddings(self) -> AzureOpenAIEmbeddings:
        """Create Azure OpenAI embeddings instance"""
        return AzureOpenAIEmbeddings(
            openai_api_key=self.api_key,
            deployment="cubeone-embedding-deployment",
            openai_api_version=self.version,
            azure_endpoint=self.endpoint,
            openai_api_type="azure"
        )

    def initialize_langchain(self) -> RetrievalQA:
        """Initialize or get the QA chain with the current vector store"""
        if not self.vectorstore:
            # Initialize with empty vector store if none exists
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )

        # Create RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.client,
            retriever=self.vectorstore.as_retriever()
        )

        return qa_chain

    def load_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        """Load documents into the vector store"""
        # Create or update vector store
        self.vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.persist_directory
        )
        
        # Save metadata for reference
        self._save_metadata(texts, metadatas)
        
        return self.vectorstore

    def _save_metadata(self, texts: List[str], metadatas: Optional[List[dict]], 
                      filename: str = "vector_store_metadata.json"):
        """Save metadata about stored documents"""
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "num_documents": len(texts),
            "document_sample": texts[:3] if texts else [],  # Save first 3 documents as sample
            "sources": [m.get("source") for m in metadatas[:3]] if metadatas else []
        }
        
        os.makedirs(self.persist_directory, exist_ok=True)
        metadata_path = os.path.join(self.persist_directory, filename)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)