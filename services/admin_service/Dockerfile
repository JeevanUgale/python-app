FROM python:3.11-slim

COPY . /app

WORKDIR /app/

RUN pip install --upgrade pip && pip install -r services/admin_service/requirements.txt


CMD ["python", "app.py"]
