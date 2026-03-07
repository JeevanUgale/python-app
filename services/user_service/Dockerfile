FROM python:3.11-slim

COPY . .

WORKDIR /app/services/user_service

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "app.py"]