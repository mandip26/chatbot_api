# api/services/embeddings.py
import os
import sys
import traceback
from functools import lru_cache
from django.conf import settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


class EmbeddingService:
    """Service for handling vectorstore and embeddings operations"""

    @staticmethod
    @lru_cache(maxsize=1)
    def get_vectorstore():
        """Load the vector store from disk with caching for performance"""
        try:
            print("Loading embeddings model...")
            embedding_model = HuggingFaceEmbeddings(
                model_name=settings.OLLAMA_QA['EMBEDDING_MODEL']
            )

            vectorstore_path = settings.OLLAMA_QA['VECTORSTORE_PATH']
            print(f"Loading vector store from {vectorstore_path}...")
            if not os.path.exists(vectorstore_path):
                error_msg = f"Vector store not found at {vectorstore_path}"
                print(f"ERROR: {error_msg}")
                raise FileNotFoundError(error_msg)

            db = FAISS.load_local(
                vectorstore_path,
                embedding_model,
                allow_dangerous_deserialization=True
            )
            print("Vector store loaded successfully!")
            return db
        except Exception as e:
            error_msg = f"Failed to load vector store: {str(e)}"
            print(f"ERROR: {error_msg}")
            traceback.print_exc()
            raise

    @staticmethod
    def get_retriever():
        """Get a configured retriever from the vectorstore"""
        vectorstore = EmbeddingService.get_vectorstore()
        retrieval_k = settings.OLLAMA_QA['RETRIEVAL_K']

        return vectorstore.as_retriever(
            search_type="mmr",  # Using Maximum Marginal Relevance for better diversity
            search_kwargs={
                'k': retrieval_k,
                'fetch_k': retrieval_k * 2,  # Fetch more candidates for MMR
                'lambda_mult': 0.7  # Balance between relevance and diversity
            }
        )