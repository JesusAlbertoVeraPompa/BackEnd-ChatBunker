# 🛡️ ChatBunker — Backend E2EE (Extreme Privacy)

**ChatBunker** es un backend de mensajería privada de alta seguridad, diseñado bajo el principio de "Zero Knowledge". El servidor nunca tiene acceso al contenido en texto plano de los mensajes, garantizando privacidad total mediante cifrado de extremo a extremo (E2EE).

---

## 🔐 Pilares de Seguridad

*   **Cifrado E2EE (Zero Knowledge):** Implementa intercambio de llaves Diffie-Hellman en el cliente. El backend solo almacena *ciphertext*.
*   **WebSockets con Seguridad Activa:** Comunicación bidireccional mediante **Django Channels** (ASGI), protegida con autenticación JWT y Rate Limiting.
*   **Borrado por Consenso:** Un mensaje solo se elimina físicamente de la base de datos cuando ambos participantes confirman la solicitud de borrado, manteniendo la integridad de la conversación.
*   **Media Assets Cifrados:** Los archivos multimedia (audios/imágenes) se almacenan cifrados en disco y se sirven mediante **URLs firmadas** de corta duración.
*   **Autenticación Robusta:** JWT con rotación de tokens, soporte para Social Login (Google/Facebook) y verificación de identidad.

---

## 🛠️ Stack Tecnológico

*   **Framework:** Django 4.2 + Django Rest Framework (DRF)
*   **Real-time:** Django Channels + Daphne (ASGI)
*   **Base de Datos:** MySQL (Persistencia de usuarios y mensajes cifrados)
*   **Capa de Mensajería:** Redis (Channel Layer para WebSockets)
*   **Seguridad:** SimpleJWT, CORS Headers, Whitenoise, Argon2/PBKDF2.
*   **Despliegue:** Optimizado para Render.com con Docker/Python.

---

## 📁 Estructura del Proyecto

```text
ChatBunker/
├── apps/
│   ├── accounts/       # Identidad, registro y verificación (JWT/Social)
│   ├── chat/           # Lógica E2EE, WebSockets (Consumers) y Media
│   ├── core/           # Middlewares de seguridad, excepciones y respuestas estándar
│   └── users/          # Gestión de perfiles y búsqueda segura de contactos
├── config/             # Configuración dual (ASGI/WSGI) y settings por entorno
├── tests/              # Suite de pruebas unitarias (PyTest)
└── requirements.txt    # Dependencias de producción y desarrollo
```

---

## 🚀 Endpoints Principales

### 💬 Chat & Mensajería
*   `GET  /api/v1/chat/conversations/` - Lista chats activos.
*   `POST /api/v1/chat/conversations/` - Inicia un nuevo chat con un usuario.
*   `GET  /api/v1/chat/conversations/{id}/history/` - Historial de mensajes filtrado por borrado.
*   `WS   /ws/chat/{conversation_id}/` - Canal de comunicación en tiempo real (E2EE).

### 👥 Usuarios
*   `GET  /api/v1/users/search/?q={email}` - Buscador de usuarios para nuevos chats.
*   `GET  /api/v1/users/me/` - Perfil del usuario autenticado.

---

## ☁️ Guía de Despliegue (Render.com)

1. **Base de Datos:** Configura una instancia de **MySQL**.
2. **Redis:** Crea un servicio de Redis para manejar los WebSockets.
3. **Web Service en Render:**
   - **Root Directory:** `BackEnd-Django`
   - **Build Command:** `./build.sh`
   - **Start Command:** `daphne -b 0.0.0.0 -p $PORT config.asgi:application`
4. **Variables de Entorno Clave:**
   - `DJANGO_SETTINGS_MODULE`: `config.settings.production`
   - `DATABASE_URL`: URL de tu MySQL.
   - `REDIS_URL`: URL interna de tu Redis.
   - `CORS_ALLOWED_ORIGINS`: URL de tu frontend (ej. GitHub Pages).

---

## 💻 Instalación Local

```bash
# 1. Clonar y entrar a la carpeta
cd BackEnd-Django

# 2. Crear y activar venv
python -m venv venv
source venv/bin/activate # O venv\Scripts\activate en Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env y Migrar
python manage.py migrate

# 5. Iniciar Servidor ASGI
daphne -b 127.0.0.1 -p 8000 config.asgi:application
```
