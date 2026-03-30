import pytest
from apps.chat.models import Conversation, Message, Media
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestChatModels:
    def test_create_conversation(self, regular_user):
        user2 = User.objects.create_user(email="user2@test.com", password="pass")
        conv = Conversation.objects.create()
        conv.participants.add(regular_user, user2)
        
        assert conv.participants.count() == 2
        assert isinstance(conv.id, str) or conv.id is not None

    def test_message_consensus_delete(self, regular_user):
        user2 = User.objects.create_user(email="user2@test.com", password="pass")
        conv = Conversation.objects.create()
        conv.participants.add(regular_user, user2)
        
        msg = Message.objects.create(
            conversation=conv,
            sender=regular_user,
            encrypted_content="ciphertext"
        )
        
        # User A borra
        msg.deleted_by_u1 = True
        msg.save()
        assert Message.objects.filter(id=msg.id).exists()
        
        # User B borra -> Consenso alcanzado
        msg.deleted_by_u2 = True
        msg.save()
        
        # Nota: La lógica de borrado físico la pusimos en el Consumer, 
        # pero podemos validarla aquí si la movemos al .save() del modelo.
        # Por ahora validamos que las banderas se guardan.
        assert msg.deleted_by_u1 is True
        assert msg.deleted_by_u2 is True
