# VERSION 2.8.3
# AUTHOR: John Omole
# DESCRIPTION: Distributed Airflow Contianer

FROM apache/airflow:slim-2.8.3-python3.11
LABEL maintainer="JohnOMDev"

# Airflow
ARG AIRFLOW_USER_HOME=/usr/local/airflow
ARG AIRFLOW_DEPS=""
ARG PYTHON_DEPS=""
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}


COPY ./requirements.txt /requirements.txt

RUN set -ex \
    && buildDeps=' \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        git \
    ' \
    && pip install --upgrade pip  && pip install -U pip setuptools wheel && pip install psycopg2-binary \
    && pip install flask-bcrypt && pip install connexion[swagger-ui] && pip install redis==5.0.3 && pip install awscli \
    && pip install -r /requirements.txt

USER root 

COPY  --chown=root scripts/entrypoint.sh ${AIRFLOW_USER_HOME}/entrypoint.sh
COPY  --chown=root scripts/airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg


# Set up a non-root user
# RUN useradd -ms /bin/bash airflow --uid 50000

RUN chown -R airflow: ${AIRFLOW_USER_HOME}

USER airflow

EXPOSE 8080 5555 8793

WORKDIR ${AIRFLOW_USER_HOME}

RUN chmod +x ${AIRFLOW_USER_HOME}/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["webserver"]
