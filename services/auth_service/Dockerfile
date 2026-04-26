FROM python:3.11-slim

COPY . /app

WORKDIR /app

ENV PYTHONPATH=/app

RUN pip install --upgrade pip && pip install -r services/auth_service/requirements.txt

CMD ["python", "services/auth_service/app.py"]