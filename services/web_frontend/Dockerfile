FROM python:3.11-slim

COPY . /app

WORKDIR /app/services/web_frontend

RUN pip install --upgrade pip && pip install -r services/web_frontend/requirements.txt

CMD ["python", "app.py"]