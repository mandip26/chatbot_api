# api/views.py
import time
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import QuerySerializer, ResponseSerializer
from api.services.retrieval import RetrievalService

logger = logging.getLogger(__name__)


class QueryView(APIView):
    """API endpoint for querying the Ollama QA system"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Send a question to the QA system and get an answer",
        request_body=QuerySerializer,
        responses={
            200: ResponseSerializer,
            400: "Bad request - Invalid input",
            401: "Unauthorized - Authentication required",
            429: "Too many requests - Rate limit exceeded",
            500: "Server error - Processing failed"
        },
        operation_id="create_query"
    )
    @method_decorator(ratelimit(key='user_or_ip', rate='10/minute', method='POST'))
    def post(self, request):
        """Process a question and return the answer with sources"""
        # Validate input
        serializer = QuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Process query
        start_time = time.time()
        try:
            query = serializer.validated_data['query']
            logger.info(f"Processing query: {query}")

            # Get response from service
            result = RetrievalService.process_query(query)

            # Add processing time
            processing_time = time.time() - start_time
            result['processing_time'] = processing_time

            # Validate and return response
            response_serializer = ResponseSerializer(data=result)
            if response_serializer.is_valid():
                return Response(response_serializer.data)
            else:
                logger.error(f"Response validation failed: {response_serializer.errors}")
                return Response(
                    {"error": "Response validation failed", "details": response_serializer.errors},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.exception(f"Error processing query: {str(e)}")
            return Response(
                {"error": "Query processing failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """API endpoint for checking system health"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Check system health and component status",
        responses={
            200: openapi.Response(
                description="System health status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'components': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            )
        },
        operation_id="health_check"
    )
    @method_decorator(cache_page(60))  # Cache health check for 60 seconds
    def get(self, request):
        """Return system health information"""
        health_status = {
            'status': 'healthy',
            'components': {
                'api': 'available',
                'vectorstore': 'unknown',
                'llm': 'unknown'
            }
        }

        # Check vectorstore health
        try:
            from api.services.embeddings import EmbeddingService
            vectorstore = EmbeddingService.get_vectorstore()
            if vectorstore:
                health_status['components']['vectorstore'] = 'available'
        except Exception as e:
            health_status['components']['vectorstore'] = 'unavailable'
            health_status['status'] = 'degraded'
            logger.warning(f"Vectorstore health check failed: {str(e)}")

        # Check LLM health (optional)
        try:
            from api.services.llm import LLMService
            llm = LLMService.get_llm()
            if llm:
                health_status['components']['llm'] = 'available'
        except Exception as e:
            health_status['components']['llm'] = 'unavailable'
            health_status['status'] = 'degraded'
            logger.warning(f"LLM health check failed: {str(e)}")

        return Response(health_status)