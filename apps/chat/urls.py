from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:pk>/history/', views.ChatHistoryView.as_view(), name='chat-history'),
    
    # E2EE Media access
    path('media/<uuid:media_id>/sign/', views.MediaSignedUrlView.as_view(), name='media-sign'),
    path('media/download/', views.MediaDownloadView.as_view(), name='media-download'),
]
