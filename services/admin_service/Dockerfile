FROM python:3.11-slim

WORKDIR /app/admin_service

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt


CMD ["python", "app.py"]
