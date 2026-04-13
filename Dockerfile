FROM python:3.10-slim

WORKDIR /app

# Instalar pip y uv
RUN pip install --no-cache-dir --upgrade pip uv==0.5.29

# Variables de entorno para uv
ENV UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_SYNC=1

# Copiar pyproject
COPY pyproject.toml ./

# Crear lockfile e instalar dependencias
RUN uv lock
RUN uv sync --no-dev

# Copiar el resto del proyecto
COPY . .

# Sincronizar dependencias del proyecto
RUN uv sync --no-dev

# ⭐ INSTALAR SETUPTOOLS DENTRO DEL ENTORNO UV
RUN uv pip install setuptools

CMD ["uv", "run", "bot.py"]
