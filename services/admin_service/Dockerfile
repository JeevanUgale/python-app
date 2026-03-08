FROM python:3.11-slim

COPY . /app

WORKDIR /app/services/admin_service

RUN pip install --upgrade pip && pip install -r requirements.txt


CMD ["python", "app.py"]
