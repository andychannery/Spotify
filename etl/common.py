#!/usr/bin/env python
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from snowflake.sqlalchemy import URL
import logging
from snowflake.connector.pandas_tools import pd_writer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

account = os.getenv("SF_ACCOUNT_IDENTIFIER")
username = os.getenv("SF_USERNAME")
password = os.getenv("SF_PASSWORD")
# database = "spotify"
# warehouse = "computeWH"
# schema = 'public'
# role = 'accountadmin'
# region = 'AWS_CA_CENTRAL_1'

def get_engine(database: str, schema: str):
    connection_parameters = {
        'account': account,
        'database': database,
        # 'warehouse': warehouse,
        'schema': schema,
        'user': username,
        'password': password,
        # 'role': role,
        # 'region': region
    }    
    try:
        url = URL(**connection_parameters)
        engine = create_engine(url)
        logging.info(f"Creating engine: {engine}")
        return engine
    except Exception as e:
        logging.warning(f"Error occurred: {str(e)}")

def write_to_sf(engine, tbl_name, dataframe, if_exists="replace"):
    with engine.connect() as conn:
        logging.info(f"Writing to {tbl_name}...")
        dataframe.columns = map(str.upper, dataframe.columns)
        dataframe.to_sql(name=tbl_name, con=conn, if_exists=if_exists, index=False, method=pd_writer)
    