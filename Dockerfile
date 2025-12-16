# Imagen base con Python 3.12
FROM python:3.12-slim

# Variables para que Python no genere .pyc y use salida sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema (psycopg2 necesita libpq y build-essential)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código al contenedor
COPY . /app

# Crear usuario no root para ejecutar la app
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Variables por defecto
ENV DJANGO_SETTINGS_MODULE=config.settings \
    PORT=8000

# Si ya tienes STATIC_ROOT configurado, podrías hacer:
# RUN python manage.py collectstatic --noinput

# Comando de arranque: gunicorn sirviendo el WSGI de Django
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
