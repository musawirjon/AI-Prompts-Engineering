import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import AzureOpenAI
import os

class ScrappingRag:
    def __init__(self):
        self.name = "Scrapping RAG"
        self.endpoint = os.getenv("OPENAI_API_URL")
        self.API_KEY = os.getenv("OPENAI_API_KEY")
        self.MODEL_NAME = os.getenv("MODEL_NAME")
        self.VERSION = os.getenv("VERSION")
        self.client = AzureOpenAI(azure_endpoint=self.endpoint,api_version=self.VERSION,api_key=self.API_KEY)

    def initialize_faiss_index():
         # Initialize FAISS index (this will store your document embeddings)
        dimension = 1536 # Size of OpenAI embeddings
        index = faiss.IndexFlatL2(dimension) # Using L2 (Euclidean) distance for simplicity
        return index

    # Store document and embeddings in FAISS
    def store_in_faiss(text, index):
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Pretrained sentence-transformer model
        embeddings = model.encode([text])

        # Convert embeddings to float32 (required by FAISS)
        embeddings = np.array(embeddings).astype('float32')

        # Add embeddings to FAISS index
        index.add(embeddings)

    def search_faiss(query, index):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode([query]).astype('float32')

        # Perform the search in FAISS index
        _, indices = index.search(query_embedding, k=1)  # Get top 1 result
        return indices
