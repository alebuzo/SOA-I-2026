FROM python:3.11-slim

WORKDIR /app

COPY . .

# instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 5000
EXPOSE 5000

# Env
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Ejecutar la aplicación
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
