FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev 

COPY [ "requirements.txt", "./" ]

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY [ "app.py", "park.mp4", "test.py", "static/", "templates/", "models/", "data/", "coco.txt", "./" ]

EXPOSE 9696

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "app:app" ]