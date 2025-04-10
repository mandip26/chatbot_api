# api/serializers.py
from rest_framework import serializers


class QuerySerializer(serializers.Serializer):
    """Serializer for query input"""
    query = serializers.CharField(
        required=True,
        max_length=1000,
        help_text="The question to be answered by the QA system"
    )


class SourceSerializer(serializers.Serializer):
    """Serializer for source information"""
    url = serializers.URLField(help_text="Source URL")
    title = serializers.CharField(help_text="Source title")
    relevance = serializers.CharField(help_text="Relevance level (high, medium, low)")


class ResponseSerializer(serializers.Serializer):
    """Serializer for the complete QA response"""
    response = serializers.CharField(help_text="Generated answer text")
    sources = SourceSerializer(many=True, help_text="List of sources for the answer")

    # Add metadata about processing
    processing_time = serializers.FloatField(
        required=False,
        help_text="Processing time in seconds"
    )