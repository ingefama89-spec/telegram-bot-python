FROM python:3.10-slim

WORKDIR /app

# Limpiar cualquier venv previo
RUN rm -rf /app/.venv

# Instalar pip y uv
RUN pip install --no-cache-dir --upgrade pip uv==0.5.29

# Crear entorno virtual uv
RUN uv venv

# Variables de entorno para uv
ENV UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_SYNC=1

# Copiar pyproject
COPY pyproject.toml ./

# ⭐ Forzar instalación de python-telegram-bot 13.14
RUN uv pip install python-telegram-bot==13.14

# Crear lockfile e instalar dependencias
RUN uv lock
RUN uv sync --no-dev

# Copiar el resto del proyecto
COPY . .

# Sincronizar dependencias del proyecto
RUN uv sync --no-dev

# Instalar setuptools dentro del entorno uv
RUN uv pip install setuptools

CMD ["uv", "run", "bot.py"]
