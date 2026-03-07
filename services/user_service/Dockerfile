FROM python:3.11-slim

COPY . /app

WORKDIR /app/services/user_service

RUN pip install --upgrade pip && pip install -r services/user_service/requirements.txt

CMD ["python", "app.py"]