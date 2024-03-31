class SqlQueries:

    create_db_query = """ CREATE DATABASE {dbname};"""

    check_db_query = """ SELECT * FROM pg_database;"""

    create_schema_query = """ CREATE SCHEMA IF NOT EXISTS {schema_name};"""

    copy_query = """COPY temp_{tablename} {fields_tuple} FROM STDIN;"""

    delete_query_reports = """
        TRUNCATE TABLE {schema_name}.{tablename}
        """
