# Imagen base ligera (estilo minimalista que nos gusta)
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias para algunas librerías de Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements y los instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app/src

# Copiamos todo el código (incluyendo la carpeta src)
COPY . .

# Ejecutamos el bot apuntando a la ruta correcta
CMD ["python", "src/bot.py"]