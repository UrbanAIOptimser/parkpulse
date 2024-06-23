FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev

# Copy and install the Python dependencies
COPY ["requirements.txt", "./"]
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the application files and directories
COPY ["app.py", "park.mp4", "test.py", "coco.txt", "./"]
COPY ["static/", "static/"]
COPY ["templates/", "templates/"]
COPY ["models/", "models/"]
COPY ["data/", "data/"]

EXPOSE 9696

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "app:app"]