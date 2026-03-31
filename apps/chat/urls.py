from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:pk>/history/', views.ChatHistoryView.as_view(), name='chat-history'),
    
    # Invitations
    path('invitations/', views.ChatInvitationView.as_view(), name='invitation-list-create'),
    path('invitations/<uuid:pk>/accept/', views.AcceptInvitationView.as_view(), name='invitation-accept'),

    # E2EE Media access
    path('media/<uuid:media_id>/sign/', views.MediaSignedUrlView.as_view(), name='media-sign'),
    path('media/download/', views.MediaDownloadView.as_view(), name='media-download'),
]
