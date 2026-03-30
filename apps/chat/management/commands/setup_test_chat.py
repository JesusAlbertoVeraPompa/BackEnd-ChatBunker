from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.chat.models import Conversation
from django.contrib.auth.models import Group

User = get_user_model()

class Command(BaseCommand):
    help = 'Configura un entorno de chat de prueba con 2 usuarios y una conversación.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando configuración de entorno de prueba...'))

        # 1. Asegurar que existe el grupo de rol Usuario
        group, _ = Group.objects.get_or_create(name='Usuario')

        # 2. Crear usuarios (Alice y Bob)
        # Se marcan como verificados para que el CustomTokenObtainPairSerializer no bloquee el login
        alice, created = User.objects.get_or_create(
            email='alice@test.com',
            defaults={
                'first_name': 'Alice',
                'last_name': 'Tester',
                'email_verified': True,
                'phone_verified': True,
                'role': 'Usuario'
            }
        )
        if created:
            alice.set_password('pass1234')
            alice.save()
            alice.groups.add(group)
            self.stdout.write(f'✅ Usuario Alice creado (alice@test.com / pass1234)')

        bob, created = User.objects.get_or_create(
            email='bob@test.com',
            defaults={
                'first_name': 'Bob',
                'last_name': 'Tester',
                'email_verified': True,
                'phone_verified': True,
                'role': 'Usuario'
            }
        )
        if created:
            bob.set_password('pass1234')
            bob.save()
            bob.groups.add(group)
            self.stdout.write(f'✅ Usuario Bob creado (bob@test.com / pass1234)')

        # 3. Crear conversación si no existe
        conversation = Conversation.objects.filter(participants=alice).filter(participants=bob).first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(alice, bob)
            self.stdout.write(self.style.SUCCESS(f'💬 Conversación privada creada entre Alice y Bob.'))
        else:
            self.stdout.write(f'ℹ️ La conversación ya existe.')

        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📌 DATOS PARA POSTMAN:"))
        self.stdout.write(f"Conversación ID: {conversation.id}")
        self.stdout.write(f"Alice ID: {alice.id}")
        self.stdout.write(f"Bob ID:   {bob.id}")
        self.stdout.write("="*50 + "\n")
