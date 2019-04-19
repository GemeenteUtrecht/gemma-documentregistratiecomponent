from django.urls import path

from .views import DownloadFileView

urlpatterns = [
    path('content/<str:inhoud>', DownloadFileView.as_view(), name='cmis-document-download'),
]
