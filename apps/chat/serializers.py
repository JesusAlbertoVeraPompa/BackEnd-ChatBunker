from rest_framework import serializers
from .models import Conversation, Message, Media, ChatInvitation
from apps.users.serializers import UserDetailSerializer

class ChatInvitationSerializer(serializers.ModelSerializer):
    sender = UserDetailSerializer(read_only=True)
    receiver = UserDetailSerializer(read_only=True)

    class Meta:
        model = ChatInvitation
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_email', 'encrypted_content', 
            'message_type', 'timestamp', 'is_mine'
        ]

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request:
            return obj.sender == request.user
        return False

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserDetailSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'last_message', 'created_at']

    def get_last_message(self, obj):
        # Solo muestra el último mensaje que no haya sido borrado por el usuario actual
        user = self.context.get('request').user
        participants = list(obj.participants.order_by('id'))
        
        is_u1 = (user == participants[0])
        
        last_msg = obj.messages.all().order_by('-timestamp').first()
        if not last_msg:
            return None
            
        # Lógica de ocultamiento por borrado individual (Consenso)
        if (is_u1 and last_msg.deleted_by_u1) or (not is_u1 and last_msg.deleted_by_u2):
            return {"detail": "Mensaje eliminado"}
            
        return MessageSerializer(last_msg, context=self.context).data
