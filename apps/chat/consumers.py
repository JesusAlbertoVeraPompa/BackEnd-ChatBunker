import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import PermissionDenied
from .models import Conversation, Message

class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer asíncrono para mensajería privada con E2EE.
    """
    async def connect(self):
        # 1. Verificar autenticación desde el middleware
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return

        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"chat_{self.conversation_id}"

        # 2. Verificar que el usuario pertenece a la conversación
        if not await self.is_participant():
            await self.close()
            return

        # 3. Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'send_message':
            # Guardar el mensaje (ciphertext) y retransmitir
            message_obj = await self.save_message(data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': str(message_obj.id),
                    'sender': str(self.user.id),
                    'content': data['encrypted_content'],
                    'msg_type': data.get('type', 'Text'),
                    'timestamp': str(message_obj.timestamp)
                }
            )

        elif action == 'key_exchange':
            # Facilitar el intercambio de llaves públicas DH (E2EE)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'relay_key',
                    'sender': str(self.user.id),
                    'public_key': data['public_key']
                }
            )

        elif action == 'request_delete':
            # Iniciar borrado por consenso
            status = await self.handle_delete_request(data.get('message_id'))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'delete_notification',
                    'message_id': data.get('message_id'),
                    'deleted_by': str(self.user.id),
                    'is_permanent': status['is_permanent']
                }
            )

    # ── Handlers de Grupo ─────────────────────────────────────────────

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def relay_key(self, event):
        # El receptor deriva el secreto compartido localmente
        if event['sender'] != str(self.user.id):
            await self.send(text_data=json.dumps(event))

    async def delete_notification(self, event):
        await self.send(text_data=json.dumps(event))

    # ── Métodos de Base de Datos ──────────────────────────────────────

    @database_sync_to_async
    def is_participant(self):
        return Conversation.objects.filter(
            id=self.conversation_id, 
            participants=self.user
        ).exists()

    @database_sync_to_async
    def save_message(self, data):
        conversation = Conversation.objects.get(id=self.conversation_id)
        return Message.objects.create(
            conversation=conversation,
            sender=self.user,
            encrypted_content=data['encrypted_content'],
            message_type=data.get('type', 'Text')
        )

    @database_sync_to_async
    def handle_delete_request(self, message_id):
        """
        Lógica de borrado por consenso.
        Si ambos confirman, se elimina. Si solo uno, se marca para ocultar.
        """
        msg = Message.objects.get(id=message_id)
        participants = list(msg.conversation.participants.order_by('id'))
        
        # Identificar si el usuario es u1 o u2 según el orden de UUID
        is_u1 = (self.user == participants[0])
        
        if is_u1:
            msg.deleted_by_u1 = True
        else:
            msg.deleted_by_u2 = True
        
        msg.save()

        # Si ambos han solicitado el borrado, se elimina el registro
        is_permanent = msg.deleted_by_u1 and msg.deleted_by_u2
        if is_permanent:
            msg.delete()
            
        return {'is_permanent': is_permanent}
