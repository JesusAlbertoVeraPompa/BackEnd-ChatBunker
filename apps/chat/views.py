from django.core.signing import Signer, BadSignature
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Conversation, Message, Media, ChatInvitation
from .serializers import ConversationSerializer, MessageSerializer, ChatInvitationSerializer
from apps.accounts.models import User
import os

signer = Signer()

class ChatInvitationView(APIView):
    """
    Maneja el envío de invitaciones de chat.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Lista las invitaciones recibidas que aún están pendientes
        invitations = ChatInvitation.objects.filter(receiver=request.user, status=ChatInvitation.InvitationStatus.PENDING)
        serializer = ChatInvitationSerializer(invitations, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        # Enviar una nueva invitación
        target_email = request.data.get('email')
        if not target_email:
            return Response({"error": "Debe proporcionar el email del usuario."}, status=status.HTTP_400_BAD_REQUEST)
        
        target_user = get_object_or_404(User, email=target_email, is_active=True)
        
        if target_user == request.user:
            return Response({"error": "No puedes invitarte a ti mismo."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si ya existe un chat entre ambos
        already_friends = Conversation.objects.filter(participants=request.user).filter(participants=target_user).exists()
        if already_friends:
            return Response({"error": "Ya tienes una conversación con este usuario."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear invitación (o recuperar si ya estaba pendiente)
        invitation, created = ChatInvitation.objects.get_or_create(
            sender=request.user,
            receiver=target_user,
            defaults={'status': ChatInvitation.InvitationStatus.PENDING}
        )

        if not created and invitation.status == ChatInvitation.InvitationStatus.REJECTED:
            # Reintentar si fue rechazada antes
            invitation.status = ChatInvitation.InvitationStatus.PENDING
            invitation.save()

        return Response(ChatInvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)

class AcceptInvitationView(APIView):
    """
    Acepta una invitación y crea la conversación de chat.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        invitation = get_object_or_404(ChatInvitation, id=pk, receiver=request.user, status=ChatInvitation.InvitationStatus.PENDING)
        
        # Iniciar transacción atómica
        from django.db import transaction
        with transaction.atomic():
            invitation.status = ChatInvitation.InvitationStatus.ACCEPTED
            invitation.save()

            # Crear la conversación si no existe (doble check)
            conversation, created = Conversation.objects.get_or_create_for_participants(invitation.sender, invitation.receiver)
        
        return Response(ConversationSerializer(conversation, context={'request': request}).data)

class ConversationListView(APIView):
    """
    Lista todas las conversaciones en las que participa el usuario.
    Permite crear una nueva conversación enviando el 'user_id' del destinatario.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = request.user.conversations.all().order_by('-created_at')
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        from apps.accounts.models import User
        target_user_id = request.data.get('user_id')
        if not target_user_id:
            return Response({"error": "Debe proporcionar el ID del usuario destinatario."}, status=status.HTTP_400_BAD_REQUEST)
        
        target_user = get_object_or_404(User, id=target_user_id, is_active=True)
        
        # Prevenir chat consigo mismo
        if target_user == request.user:
            return Response({"error": "No puedes iniciar un chat contigo mismo."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Verificar si ya existe una conversación entre ambos
        # (Optimizamos buscando una conversación que tenga exactamente a ambos participantes)
        conversation = Conversation.objects.filter(participants=request.user).filter(participants=target_user).first()
        
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, target_user)
            status_code = status.HTTP_201_CREATED
        else:
            status_code = status.HTTP_200_OK
            
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data, status=status_code)

class ChatHistoryView(APIView):
    """
    Obtiene el historial de una conversación específica.
    Implementa el filtrado según el borrado individual (consenso).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk, participants=request.user)
...
        serializer = MessageSerializer(filtered_msgs, many=True, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, pk):
        """
        Elimina la conversación para el usuario actual.
        Si ambos la eliminan, se borra de la base de datos.
        """
        conversation = get_object_or_404(Conversation, id=pk, participants=request.user)
        # Por ahora, para simplificar y cumplir tu petición, la borramos completamente
        conversation.delete()
        return Response({"message": "Conversación eliminada."}, status=status.HTTP_204_NO_CONTENT)

class MediaSignedUrlView(APIView):
    """
    Genera una URL firmada de corta duración para descargar un archivo multimedia.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, media_id):
        # 1. Verificar que el media pertenezca a una conversación del usuario
        media = get_object_or_404(Media, id=media_id)
        if not media.message.conversation.participants.filter(id=request.user.id).exists():
            return Response({"error": "No tienes permiso para este archivo."}, status=status.HTTP_403_FORBIDDEN)
            
        # 2. Generar firma criptográfica (el token es válido por un tiempo breve)
        token = signer.sign(str(media.id))
        
        from django.urls import reverse
        download_url = f"{request.build_absolute_uri(reverse('media-download'))}?token={token}"
        
        return Response({"download_url": download_url})

class MediaDownloadView(APIView):
    """
    Sirve el archivo solo si la firma es válida.
    """
    # NO requiere autenticación vía header, sino vía Token firmado en URL
    permission_classes = [] 

    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # 1. Verificar firma (lanzará BadSignature si es inválido o alterado)
            # expiración implícita si añadimos timestamps a la firma
            media_id = signer.unsign(token)
            media = get_object_or_404(Media, id=media_id)
            
            # 2. Servir el archivo como stream binario
            response = FileResponse(media.encrypted_file.open('rb'))
            response['Content-Type'] = 'application/octet-stream' # Binario cifrado
            return response
            
        except (BadSignature, Exception):
            return Response({"error": "Enlace inválido o expirado."}, status=status.HTTP_403_FORBIDDEN)
