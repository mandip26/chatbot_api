# api/services/llm.py
from functools import lru_cache
from django.conf import settings
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate


class LLMService:
    """Service for handling LLM operations"""

    @staticmethod
    @lru_cache(maxsize=1)
    def get_llm():
        """Initialize and cache the Ollama LLM"""
        print(f"Loading Ollama LLM ({settings.OLLAMA_QA['LLM_MODEL']})...")
        return OllamaLLM(
            model=settings.OLLAMA_QA['LLM_MODEL'],
            temperature=settings.OLLAMA_QA['TEMPERATURE']
        )

    @staticmethod
    def create_qa_prompt():
        """Create an optimized prompt template for the QA chain"""
        qa_template = """
        ### Context Information:
        {context}

        ### Question:
        {question}

        ### Instructions:
        - Answer using only information from the provided context
        - If the answer is not in the context, respond with "I don't have enough information to answer this question"
        - Be concise but thorough
        - When appropriate, reference source URLs from the context
        - Format any technical information clearly
        - Avoid making assumptions beyond what's stated in the context

        ### Answer:
        """

        return PromptTemplate(template=qa_template, input_variables=["context", "question"])