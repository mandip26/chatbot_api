# api/apps.py
from django.apps import AppConfig
import os
from django.conf import settings

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """Validate required paths and preload models when ready"""
        # Only perform checks in the primary process (avoid duplicate loading with auto-reload)
        if os.environ.get('RUN_MAIN') != 'true':
            # Validate that the vectorstore path exists
            vectorstore_path = settings.OLLAMA_QA['VECTORSTORE_PATH']
            if not os.path.exists(vectorstore_path):
                print(f"WARNING: Vector store not found at {vectorstore_path}")
                print("Please run the vectorstore creation script before using the API.")
            else:
                # Optional - preload models in another thread to speed up first request
                # We'll use lazy loading instead to avoid slowing down startup
                pass