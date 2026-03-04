FROM python:3.11-slim

WORKDIR /app/services/auth_service

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "app.py"]