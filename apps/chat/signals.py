import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Media, Conversation

@receiver(post_delete, sender=Media)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Elimina físicamente el archivo cifrado del almacenamiento al borrar el modelo Media.
    """
    if instance.encrypted_file:
        if os.path.isfile(instance.encrypted_file.path):
            os.remove(instance.encrypted_file.path)

@receiver(post_delete, sender=Conversation)
def cleanup_conversation_media(sender, instance, **kwargs):
    """
    Asegura la limpieza total al borrar una conversación.
    """
    # Los mensajes se borran por CASCADE, lo que disparará el borrado de Media
    pass
