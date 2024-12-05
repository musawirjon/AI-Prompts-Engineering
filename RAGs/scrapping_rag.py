import faiss
import numpy as np
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureOpenAI
import os
import json

class ScrappingRag:
    def __init__(self):
        self.name = "Scrapping RAG"
        self.endpoint = os.getenv("OPENAI_API_URL")
        self.API_KEY = os.getenv("OPENAI_API_KEY")
        self.MODEL_NAME = os.getenv("MODEL_NAME")
        self.VERSION = os.getenv("VERSION")
        self.client = AzureOpenAI(azure_endpoint=self.endpoint, api_version=self.VERSION, api_key=self.API_KEY)

    def get_embeddings(self, text_data):
        embeddings = AzureOpenAIEmbeddings(
            openai_api_key=self.API_KEY,
            deployment="cubeone-embedding-deployment",  # Deployment should match the embedding model used
            openai_api_version=self.VERSION,
            azure_endpoint=self.endpoint,
            openai_api_type="azure"
        )

        text_embeddings = embeddings.embed_documents(text_data)
        return text_embeddings
    
    def create_faiss_index(self, texts):
        embeddings = self.get_embeddings(texts)
        self.save_embeddings_to_json(embeddings, texts)  # Save embeddings to JSON

        index = faiss.IndexFlatL2(len(embeddings[0]))
        index.add(np.array(embeddings))
        index_path = index_path="faiss_index.index"
        faiss.write_index(index, index_path)
        return index

    def save_embeddings_to_json(self, embeddings, texts, filename="embeddings.json"):
        data = {
            "embeddings": embeddings,
            "texts": texts
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
