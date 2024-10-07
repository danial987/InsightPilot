import io  # Ensure you import io to handle in-memory binary streams
import pandas as pd
import json
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, LargeBinary, DateTime, Index
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool
import datetime
import streamlit as st
import time
from cachetools import cached, TTLCache

# username = "postgres.qshtpwzpnifujdbwteqe"
# password = "Insightpilot3421$"
# host = "aws-0-ap-southeast-1.pooler.supabase.com"
# port = "6543"
# database = "postgres"

# Database configuration
db_config = st.secrets["connections"]["postgresql"]
DATABASE_URL = f"postgresql+psycopg2://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

# Create engine and metadata
engine = create_engine(DATABASE_URL, poolclass=QueuePool, pool_size=10, max_overflow=20)
metadata = MetaData()


# Define cache with TTL
cache = TTLCache(maxsize=100, ttl=300)  # Cache up to 100 queries for 5 minutes

# Define Dataset class
class Dataset:
    def __init__(self):
        self.datasets = Table(
            'datasets', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String, nullable=False),
            Column('file_format', String, nullable=False),
            Column('file_size', Integer, nullable=False),
            Column('upload_date', DateTime, default=datetime.datetime.utcnow),
            Column('data', LargeBinary, nullable=False),
            Column('last_accessed', DateTime, default=datetime.datetime.utcnow),
            extend_existing=True
        )
        Index('idx_last_accessed', self.datasets.c.last_accessed)
        Index('idx_name', self.datasets.c.name)
        metadata.create_all(engine)

    session = scoped_session(sessionmaker(bind=engine))

    def save_to_database(self, file_name, file_format, file_size, data):
        start_time = time.time()
        self.session.execute(self.datasets.insert().values(
            name=file_name, file_format=file_format, file_size=file_size, data=data, last_accessed=datetime.datetime.utcnow()))
        self.session.commit()
        print(f"Insert operation took {time.time() - start_time} seconds")

    @cached(cache)
    def fetch_datasets(self):
        start_time = time.time()
        result = self.session.execute(self.datasets.select().order_by(self.datasets.c.last_accessed.desc())).fetchall()
        print(f"Fetch operation took {time.time() - start_time} seconds")
        return result

    def delete_dataset(self, dataset_id):
        start_time = time.time()
        self.session.execute(self.datasets.delete().where(self.datasets.c.id == dataset_id))
        self.session.commit()
        print(f"Delete operation took {time.time() - start_time} seconds")

    @cached(cache)
    def get_dataset_by_id(self, dataset_id):
        start_time = time.time()
        result = self.session.execute(self.datasets.select().where(self.datasets.c.id == dataset_id)).fetchone()
        print(f"Get operation took {time.time() - start_time} seconds")
        return result


   
    def update_last_accessed(self, dataset_id):
        start_time = time.time()
        self.session.execute(self.datasets.update().where(self.datasets.c.id == dataset_id).values(last_accessed=datetime.datetime.utcnow()))
        self.session.commit()
        print(f"Update operation took {time.time() - start_time} seconds")

    def rename_dataset(self, dataset_id, new_name):
        start_time = time.time()
        self.session.execute(self.datasets.update().where(self.datasets.c.id == dataset_id).values(name=new_name))
        self.session.commit()
        print(f"Rename operation took {time.time() - start_time} seconds")

    def dataset_exists(self, file_name):
        start_time = time.time()
        result = self.session.execute(self.datasets.select().where(self.datasets.c.name == file_name)).fetchone()
        print(f"Exist check operation took {time.time() - start_time} seconds")
        return result is not None

    @staticmethod
    def try_parsing_csv(uploaded_file):
        start_time = time.time()
        try:
            data = pd.read_csv(uploaded_file)
            print(f"CSV parsing took {time.time() - start_time} seconds")
            return data
        except pd.errors.ParserError as e:
            st.error(f"Error parsing the CSV file: {e}")
            return None

    @staticmethod
    def try_parsing_json(uploaded_file):
        start_time = time.time()
        try:
            data = uploaded_file.read().decode('utf-8').strip().split('\n')
            json_data = [json.loads(line) for line in data if line.strip()]
            result = pd.json_normalize(json_data)
            print(f"JSON parsing took {time.time() - start_time} seconds")
            return result
        except json.JSONDecodeError as e:
            st.error(f"Error parsing the JSON file: {e}")
            return None
        except Exception as e:
            st.error(f"Error parsing the JSON file: {e}")
            return None

    @classmethod
    def close_session(cls):
        cls.session.remove()

Dataset.close_session()