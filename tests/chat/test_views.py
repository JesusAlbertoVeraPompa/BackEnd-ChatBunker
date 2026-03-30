import pytest
from django.urls import reverse
from rest_framework import status
from apps.chat.models import Conversation, Message

@pytest.mark.django_db
class TestChatViews:
    def test_get_conversations(self, auth_client, regular_user):
        conv = Conversation.objects.create()
        conv.participants.add(regular_user)
        
        url = reverse('conversation-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_history_forbidden(self, auth_client):
        # Otro usuario crea una conv en la que no estoy
        conv = Conversation.objects.create()
        url = reverse('chat-history', kwargs={'pk': conv.id})
        response = auth_client.get(url)
        
        # Debo recibir 404 (porque get_object_or_404 filtra por participantes)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_history_hides_deleted_messages(self, auth_client, regular_user):
        conv = Conversation.objects.create()
        conv.participants.add(regular_user)
        
        # u1: user (UUID menor o mayor) - asumamos u1
        # Creamos un mensaje marcado como borrado por u1
        Message.objects.create(
            conversation=conv,
            sender=regular_user,
            encrypted_content="invisible",
            deleted_by_u1=True # Supongamos que soy u1
        )
        
        # Este no está borrado
        Message.objects.create(
            conversation=conv,
            sender=regular_user,
            encrypted_content="visible",
            deleted_by_u1=False
        )
        
        url = reverse('chat-history', kwargs={'pk': conv.id})
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Solo debe ver 1 mensaje (aunque hay 2 en la BD para esa conv)
        assert len(response.data) == 1
        assert response.data[0]['encrypted_content'] == "visible"
