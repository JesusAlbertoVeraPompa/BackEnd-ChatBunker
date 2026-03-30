#!/bin/bash
# ─────────────────────────────────────────
# deploy_cpanel.sh — Script de Automatización
# ─────────────────────────────────────────

# 1. Rutas (¡IMPORTANTE: Actualiza según tu cPanel!)
PROJECT_ROOT="/home/TU_USUARIO/ChatBunker"
VENV_PATH="/home/TU_USUARIO/virtualenv/ChatBunker/3.11/bin/activate"
PYTHON_BIN="/home/TU_USUARIO/virtualenv/ChatBunker/3.11/bin/python"

echo "🚀 Iniciando despliegue de Chat E2EE en cPanel..."

# 2. Entrar al proyecto
cd $PROJECT_ROOT || { echo "❌ Error: No se encontró la carpeta del proyecto."; exit 1; }

# 3. Activar el entorno virtual
source $VENV_PATH

# 4. Instalar/Actualizar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
pip install daphne channels channels-redis django-extensions

# 5. Aplicar migraciones
echo "🗄️ Aplicando migraciones..."
$PYTHON_BIN manage.py makemigrations chat
$PYTHON_BIN manage.py migrate

# 6. Recoger estáticos
echo "📂 Recogiendo archivos estáticos..."
$PYTHON_BIN manage.py collectstatic --no-input

# 7. Reiniciar el servidor ASGI (WebSockets)
echo "🔌 Reiniciando servidor ASGI (Daphne)..."
# Matamos el proceso anterior si existe
pkill -f "daphne"

# Iniciamos Daphne en el puerto 8001
# nohup asegura que siga corriendo al cerrar la terminal
nohup daphne -b 127.0.0.1 -p 8001 config.asgi:application > asgi.log 2>&1 &

echo "✅ Despliegue completado. Los WebSockets están corriendo en el puerto 8001."
echo "🔗 El log está en: $PROJECT_ROOT/asgi.log"
