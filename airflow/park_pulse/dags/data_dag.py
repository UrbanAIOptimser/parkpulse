import pprint as pp
import os
import airflow.utils.dates
from airflow import DAG, macros
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.connection import Connection

postgres_conn_id = "postgres_default"
hook: PostgresHook = PostgresHook(postgres_conn_id=postgres_conn_id)
conn: Connection = hook.get_connection(conn_id=postgres_conn_id)
postgres_password = conn.password
postgres_host = conn.host
postgres_login = conn.login
postgres_port = conn.port


default_args = {
    "owner": "airflow",
    "start_date": airflow.utils.dates.days_ago(10),
}


def print_env():
    print(f"{os.environ['AIRFLOW_CTX_EXECUTION_DATE']}")
    print(f"postgres_password: {postgres_password}")
    print(f"postgres_login: {postgres_login}")
    print(f"postgres_port: {postgres_port}")
    print(f"postgres_host: {postgres_host}")


with DAG(
    dag_id="data_dag", default_args=default_args, schedule_interval="@daily"
) as dag:

    upload = DummyOperator(task_id="upload")

    process = BashOperator(task_id="process", bash_command="echo 'processing'")

    # This task will fail half the time based
    # based on the day of the execution date modulo 2
    # If day 16 % 2 = exit 0
    # If day 17 % 2 = exit 1

    print__env = PythonOperator(task_id="print__env", python_callable=print_env)
    fail = BashOperator(
        task_id="fail",
        bash_command="""
                valid={{macros.ds_format(ds, "%Y-%m-%d", "%d")}}
                if [ $(($valid % 2)) == 1 ]; then
                        exit 1
                else
                        exit 0
                fi
            """,
    )

    upload >> process >> print__env >> fail
