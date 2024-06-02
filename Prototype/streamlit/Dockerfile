FROM python:3.11-slim

ENV APP_DIR /usr/src/app


LABEL author="john"
LABEL description="Deployment of parkpulse app"

WORKDIR ${APP_DIR}

COPY requirements.txt ${APP_DIR}/

RUN pip install -r requirements.txt

COPY app.py ${APP_DIR}/

CMD ["streamlit", "run", "app.py"]