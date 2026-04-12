FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip uv==0.5.29

ENV UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_SYNC=1

COPY pyproject.toml uv.lock ./

RUN uv lock
RUN uv sync --no-dev --no-install-project

COPY . .

# ESTA ES LA LÍNEA QUE FALTABA
RUN uv sync --no-dev

CMD ["uv", "run", "bot.py"]
