import uuid
from django.db import models
from django.conf import settings

class Conversation(models.Model):
    """
    Representa una conversación privada entre dos participantes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="conversations")
    session_public_key = models.TextField(null=True, blank=True, help_text="Llave pública efímera para el intercambio DH")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"

    def __str__(self):
        return f"Chat {self.id}"

class Message(models.Model):
    """
    Mensaje cifrado de extremo a extremo (E2EE).
    El contenido almacenado es siempre ciphertext.
    """
    class MessageType(models.TextChoices):
        TEXT = "Text", "Texto"
        AUDIO = "Audio", "Audio"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    
    # E2EE: El backend nunca conoce el contenido plano
    encrypted_content = models.TextField()
    message_type = models.CharField(max_length=10, choices=MessageType.choices, default=MessageType.TEXT)
    
    # Borrado por Consenso
    # u1: Participante con el UUID menor (alfabéticamente)
    # u2: Participante con el UUID mayor
    deleted_by_u1 = models.BooleanField(default=False)
    deleted_by_u2 = models.BooleanField(default=False)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"

    def __str__(self):
        return f"Msg {self.id} de {self.sender.email}"

class Media(models.Model):
    """
    Almacenamiento de archivos binarios cifrados.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name="media")
    encrypted_file = models.FileField(upload_to="encrypted_media/%Y/%m/%d/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Archivo Multimedia"
        verbose_name_plural = "Archivos Multimedia"
