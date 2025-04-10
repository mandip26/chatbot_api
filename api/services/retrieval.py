# api/services/retrieval.py
import traceback
from functools import lru_cache
from django.conf import settings
from langchain.chains import RetrievalQA

from api.services.embeddings import EmbeddingService
from api.services.llm import LLMService


class RetrievalService:
    """Service for handling QA chain and retrieval operations"""

    @staticmethod
    @lru_cache(maxsize=1)
    def create_qa_chain():
        """Create and cache the QA chain for reuse"""
        retriever = EmbeddingService.get_retriever()
        llm = LLMService.get_llm()
        prompt = LLMService.create_qa_prompt()

        print("Creating QA chain...")
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # Using stuff as documents are small chunks
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={'prompt': prompt}
        )

    @staticmethod
    def process_query(query_text):
        """Process a query and return the response with sources"""
        try:
            print(f"Processing query: {query_text}")

            # Get cached QA chain
            qa_chain = RetrievalService.create_qa_chain()

            # Invoke chain
            print("Generating response...")
            response = qa_chain.invoke({'query': query_text})

            # Extract results
            result = response["result"]
            source_documents = response["source_documents"]

            # Process sources (with deduplication)
            sources = []
            seen_urls = set()
            for doc in source_documents:
                url = doc.metadata.get('url', '')
                title = doc.metadata.get('title', '')

                if url and url not in seen_urls:
                    seen_urls.add(url)
                    sources.append({
                        "url": url,
                        "title": title if title else url,
                        "relevance": "high" if not sources else "medium"  # Mark first source as high relevance
                    })

            return {
                "response": result,
                "sources": sources[:3]  # Limit to top 3 sources for clarity
            }
        except Exception as e:
            error_msg = f"Failed to process query: {str(e)}"
            print(f"ERROR: {error_msg}")
            traceback.print_exc()
            raise