# -*- coding: utf-8 -*-
import os
import io
import gzip
import json
import psycopg
import duckdb
import logging
import boto3
import configparser
import requests

logging.basicConfig(format="%(asctime)s %(name)s %(levelname)-10s %(message)s")
LOG = logging.getLogger(__name__)
LOG.setLevel(os.environ.get("LOG_LEVEL", logging.DEBUG))

conn = duckdb.connect()
config = configparser.ConfigParser()
config.read("./src/credentials.cfg")

class HELPER:

    def __init__(self, BASE_URL, s3_bucket, s3_raw_key, s3_processed_key):
        self.BASE_URL = BASE_URL
        self.s3_bucket = s3_bucket
        self.s3_key = s3_raw_key
        self.s3_processed_key = s3_processed_key

    def aicraft_db_parser(self, data:str) -> list[dict]:
        dict_list = []
        json_objects = data.strip().split('\n')
        for obj in json_objects:
            try:
                dict_data = json.loads(obj)
                dict_list.append(dict_data)
            except json.JSONDecodeError as e:
                print('Error decoding JSON:', e)
        return dict_list

    def fuel_consumption_parser(self, data:str) -> list[dict]:
        dict_list = []
        for key, value in data.items():
            try:
                value['type'] = key
                dict_list.append(value)
            except json.JSONDecodeError as e:
                print('Error decoding JSON:', e)
        return dict_list


    def fetch_data(self, link: str) -> str:
        """

        Parameters
        ----------
        link : str

        Returns
        -------
        str

        """
        try:
            if link:
                api_url = f"{self.BASE_URL}{link}"
            else:
                api_url = f"{self.BASE_URL}"
            response = requests.get(api_url, timeout=200)
            data = self.convert_(response)
            return data
        except requests.RequestException as e:
            LOG.error(f"Error fetching {api_url}: {e}")

    def convert_(self, r: requests.Response) -> list[dict]:
        """

        Parameters
        ----------
        r : requests.Response

        Returns
        -------
        List[dict]

        """

        try:
            data = gzip.decompress(r.content)
            return data.decode("utf-8")
        except gzip.BadGzipFile:
            return r.json()
        else:
            LOG.error(f"error {r.status_code}, {r.content}")

    def upload_file_s3(self, link: str, git:bool = False) -> None:
        """

        Parameters
        ----------
        link : str
            DESCRIPTION.

        Returns
        -------
        None
            DESCRIPTION.

        """
        
        try:
            session = boto3.Session(profile_name="bdi")
            s3 = session.client("s3")
            data = self.fetch_data(link)
            link = link.split('.')[0]
            if git and isinstance(data, dict):
                data = self.fuel_consumption_parser(data)
            if isinstance(data, str):
                data = self.aicraft_db_parser(data)
            n=25000
            if len(data) >= n:
                for i in range(0, len(data), n):
                    key = f"{self.s3_key}/{link}-{i}.json.gz"
                    compressed_data = gzip.compress(json.dumps(data[i:i+n]).encode("utf-8"))
                    s3.put_object(Body=compressed_data, Bucket=self.s3_bucket, Key=key)
            else:
                key = f"{self.s3_key}/{link}.json.gz"
                compressed_data = gzip.compress(json.dumps(data).encode("utf-8"))
                s3.put_object(Body=compressed_data, Bucket=self.s3_bucket, Key=key)
            LOG.info(f"File {key} uploaded to {self.s3_bucket}")
        except Exception as e:
            LOG.error(f"Error uploading file to s3: {e}")

    def get_file_downloaded(self, prefix, full_path=None) -> list:
        """

        Parameters
        ----------
        prefix : str
            DESCRIPTION.
        full_path : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        list
            DESCRIPTION.

        """
        try:
            session = boto3.Session(profile_name="bdi")
            s3 = session.client("s3")
            response = s3.list_objects_v2(Bucket=self.s3_bucket, Prefix=prefix)
            files = response.get("Contents", list())
            if full_path:
                data = [f's3://{self.s3_bucket}/{file.get("Key")}' for file in files]
            else:
                data = [file.get("Key") for file in files]
            return data
        except Exception as e:
            LOG.error(f"Error retrieving file from s3: {e}")

    def get_conn(self, default_db: str, dbname=None) -> tuple:
        """
   
        Parameters
        ----------
        default_db : str
            DESCRIPTION.
        dbname : TYPE, optional
            DESCRIPTION. The default is None.
   
        Returns
        -------
        tuple
            DESCRIPTION.
   
        """
        if dbname is None:
            conn = psycopg.connect(default_db)
        else:
            conn = psycopg.connect(f"dbname= {dbname} {default_db}")
        conn.autocommit = True
        cur = conn.cursor()
        return conn, cur

    def check_db(self, default_db: str, dbname: str) -> set:
         """

         Parameters
         ----------
         default_db : str
             DESCRIPTION.
         dbname : str
             DESCRIPTION.

         Returns
         -------
         set
             DESCRIPTION.

         """
         conn, cur = self.get_conn(default_db)
         try:
             pg_db = cur.execute("""SELECT * FROM pg_database""").fetchall()
             db = {row for row in pg_db if dbname in row}
             conn.commit()
         except BaseException:
             conn.rollback()
         return db

    def create_db(self, default_db: str, dbname: str) -> None:
         """

         Parameters
         ----------
         default_db : str
             DESCRIPTION.
         dbname : str
             DESCRIPTION.

         Returns
         -------
         None
             DESCRIPTION.

         """
         conn, cur = self.get_conn(default_db)
         db = self.check_db(default_db, dbname)
         if len(db) < 1:
             try:
                 cur.execute(f"""CREATE DATABASE {dbname};""")
                 conn.commit()
                 LOG.info(f"Database Successfully Created: {dbname}")
             except BaseException:
                 conn.rollback()
                 LOG.info(f"Problem Creating Database: {dbname}")

    def create_schema(self, default_db: str, dbname: str, schema_name: str) -> set:
         """

         Parameters
         ----------
         default_db : str
             DESCRIPTION.
         dbname : str
             DESCRIPTION.
         schema_name : str
             DESCRIPTION.

         Returns
         -------
         set
             DESCRIPTION.

         """
         conn, cur = self.get_conn(default_db, dbname)
         try:
             cur.execute(f"""CREATE SCHEMA IF NOT EXISTS {schema_name};""")
             conn.commit()
         except BaseException:
             conn.rollback()

    def create_tables(
         self, default_db: str, dbname: str, schema_name: str, tablename: str, sql_query: str
     ) -> None:
         """

         Parameters
         ----------
         default_db : str
             DESCRIPTION.
         dbname : str
             DESCRIPTION.
         schema_name : str
             DESCRIPTION.
         tablename : str
             DESCRIPTION.

         Returns
         -------
         None
             DESCRIPTION.

         """
         conn, cur = self.get_conn(default_db, dbname)
         try:
             cur.execute( sql_query
             )
             conn.commit()
         except BaseException:
             conn.rollback()


    def get_postgres_data(self, query: str) -> list[tuple]:
         """

         Parameters
         ----------
         query : str
             DESCRIPTION.

         Returns
         -------
         list[tuple]
             DESCRIPTION.

         """
         try:
             conn = self._duckdb()
             cursor = conn.execute(query)
             result = cursor.fetchall()
             conn.commit()
         except Exception as e:
             LOG.error("problem getting postgres data", e)
         return result

    def _duckdb(self):
         """ """
         return duckdb.connect()


    def read_parquet(self, _file_dir: str) -> None:
        """

        Parameters
        ----------
        _file_dir : str
            DESCRIPTION.

        Returns
        -------
        None
            DESCRIPTION.

        """
        try:
            duckdb.sql("INSTALL aws;")
            duckdb.sql("LOAD aws;")
            duckdb.sql("INSTALL parquet;")
            duckdb.sql("INSTALL httpfs;")
            duckdb.sql("LOAD httpfs;")
            query = f"""
            CALL load_aws_credentials('bdi');
            SET memory_limit='50GB';
            SET threads TO 4;
            SELECT * FROM read_parquet('{_file_dir}');"""
            data = duckdb.sql(query)
            records = data.fetchall()
        except Exception as e:
            LOG.error("export_parquet", e)
        return records


    def copy_data(
            self, default_db: str, dbname: str, schema_name: str, tablename: str
        ) -> None:
            """
    
            Parameters
            ----------
            default_db : str
                DESCRIPTION.
            dbname : str
                DESCRIPTION.
            schema_name : str
                DESCRIPTION.
            tablename : str
                DESCRIPTION.
    
            Returns
            -------
            None
                DESCRIPTION.
    
            """
            conn, cur = self.get_conn(default_db, dbname)
            filename_prepared = self.get_file_downloaded(
                prefix="prepared/day=20231101",
                full_path=True,
            )
            cur.execute(
                f"""
                    CREATE TEMP TABLE temp_{tablename} (
                        timestamp VARCHAR(20),
                        icao VARCHAR(7) NOT NULL,
                        type VARCHAR(20),
                        registration VARCHAR(20),
                        altitude_baro VARCHAR(20),
                        ground_speed VARCHAR(20),
                        latitude NUMERIC(10, 6),
                        longitude NUMERIC(10, 6),
                        emergency VARCHAR(10),
                        day VARCHAR(10),
                        UNIQUE (icao, timestamp)
                    );
                    """
            )
            try:
                total = 0
                for file in filename_prepared:
                    LOG.info(file)
                    records = self.read_parquet(file)
                    LOG.info(f"record pushing to table {tablename} is : {len(records)}")
                    total += len(records)
                    with cur.copy(
                        f"COPY temp_{tablename} (timestamp, icao, type, registration, \
                                                 altitude_baro, ground_speed, \
                                                 latitude, longitude, emergency, \
                                                 day) FROM STDIN"
                    ) as copy:
                        for record in records:
                            copy.write_row(record)
                conn.commit()
            except BaseException:
                conn.rollback()
    
            # Merge the data into Prod
            try:
                cur.execute(
                    f"""
                    INSERT INTO {dbname}.{schema_name}.{tablename} (
                        timestamp, icao, type, registration,
                        altitude_baro, ground_speed, latitude,
                        longitude, emergency, day
                    )
                    SELECT timestamp, icao, type, registration,
                    altitude_baro, ground_speed, latitude,
                    longitude, emergency, day
                    FROM temp_{tablename}
                    ON CONFLICT (icao, timestamp) DO UPDATE SET
                        type = EXCLUDED.type,
                        registration = EXCLUDED.registration,
                        altitude_baro = EXCLUDED.altitude_baro,
                        ground_speed = EXCLUDED.ground_speed,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        emergency = EXCLUDED.emergency,
                        day = EXCLUDED.day,
                        _fast_api_sync = current_timestamp
                """
                )
                LOG.info("Successfully Merge")
                conn.commit()
            except BaseException:
                conn.rollback()
