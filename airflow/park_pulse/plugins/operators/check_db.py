# -*- coding: utf-8 -*-
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.postgres_hook import PostgresHook

class CheckDbOperator(BaseOperator):
    """
    Operator to check if a database exists.
    """
    @apply_defaults
    def __init__(self, dbname, postgres_conn_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbname = dbname
        self.postgres_conn_id = postgres_conn_id
    def execute(self, context):
        postgres_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        # Check if the database exists
        sql = f"SELECT 1 FROM pg_database WHERE datname = '{self.dbname}'"
        connection = postgres_hook.get_conn()
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        db_exists = bool(result)
        cursor.close()
        connection.close()
        # Store the result in XCom
        context['ti'].xcom_push(key='db_exists', value=db_exists)
