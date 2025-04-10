# api/urls.py
from django.urls import path
from api.views import QueryView, HealthCheckView

urlpatterns = [
    path('v1/query', QueryView.as_view(), name='query-no-slash'),
    path('v1/query/', QueryView.as_view(), name='query'),
    path('v1/health/', HealthCheckView.as_view(), name='health'),
]