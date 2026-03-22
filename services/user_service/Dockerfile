FROM python:3.11-slim

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip && pip install -r services/user_service/requirements.txt

CMD ["python", "services/user_service/app.py"]