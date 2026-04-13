FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip uv==0.5.29

ENV UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_SYNC=1

COPY pyproject.toml ./

# Generar lockfile nuevo
RUN uv lock

# Instalar dependencias del proyecto
RUN uv sync --no-dev

# Copiar el código
COPY . .

# Instalar el proyecto completo (incluye telegram, urllib3, six, etc.)
RUN uv sync --no-dev

CMD ["uv", "run", "bot.py"]
