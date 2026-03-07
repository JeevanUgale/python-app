FROM python:3.11-slim

COPY . .

WORKDIR /app/services/auth_service

RUN pip install --upgrade pip && pip install -r services/auth_service/requirements.txt

CMD ["python", "app.py"]