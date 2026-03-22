FROM python:3.11-slim

COPY . /app

WORKDIR /app

ENV PYTHONPATH=/app

RUN pip install --upgrade pip && pip install -r services/web_frontend/requirements.txt

CMD ["python", "services/web_frontend/app.py"]