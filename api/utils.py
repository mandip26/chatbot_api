# api/utils.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Custom exception handler for better error responses"""
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If response is None, it's an unhandled exception
    if response is None:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return Response(
            {
                'error': 'An unexpected error occurred',
                'detail': str(exc) if not isinstance(exc, Exception) else str(exc),
                'type': exc.__class__.__name__
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Add more details to the response
    if isinstance(response.data, dict):
        if 'detail' in response.data:
            response.data['message'] = response.data['detail']

        response.data['type'] = exc.__class__.__name__

    return response