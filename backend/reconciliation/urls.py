from django.urls import path
from .views import reconciliation_api

urlpatterns = [
    path("reconciliation/", reconciliation_api, name="reconciliation-api"),
]