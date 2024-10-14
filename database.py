import io
import pandas as pd
import json
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, LargeBinary, DateTime, ForeignKey, Index
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool
import datetime
import streamlit as st
import time
from cachetools import cached, TTLCache

# Database configuration
db_config = st.secrets["connections"]["postgresql"]
DATABASE_URL = f"postgresql+psycopg2://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

# Create engine and metadata
engine = create_engine(DATABASE_URL, poolclass=QueuePool, pool_size=10, max_overflow=20)
metadata = MetaData()

# Define cache with TTL
cache = TTLCache(maxsize=100, ttl=300)  # Cache up to 100 queries for 5 minutes

# Define Dataset class with user-specific dataset handling
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
            Column('user_id', Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),  # Link datasets to users
            extend_existing=True
        )
        Index('idx_last_accessed', self.datasets.c.last_accessed)
        Index('idx_name', self.datasets.c.name)
        metadata.create_all(engine)

    session = scoped_session(sessionmaker(bind=engine))

    def save_to_database(self, file_name, file_format, file_size, data, user_id):
        """
        Save a new dataset to the database for the specified user.
        """
        start_time = time.time()
        self.session.execute(self.datasets.insert().values(
            name=file_name, 
            file_format=file_format, 
            file_size=file_size, 
            data=data, 
            user_id=user_id,  # Assign the dataset to a user
            last_accessed=datetime.datetime.utcnow()))
        self.session.commit()
        print(f"Insert operation took {time.time() - start_time} seconds")

    @cached(cache)
    def fetch_datasets(self, user_id):
        """
        Fetch all datasets owned by the specified user.
        """
        start_time = time.time()
        result = self.session.execute(
            self.datasets.select().where(self.datasets.c.user_id == user_id).order_by(self.datasets.c.last_accessed.desc())
        ).fetchall()
        print(f"Fetch operation took {time.time() - start_time} seconds")
        return result

    def delete_dataset(self, dataset_id, user_id):
        """
        Delete a dataset owned by the specified user.
        """
        start_time = time.time()
        self.session.execute(
            self.datasets.delete().where(self.datasets.c.id == dataset_id).where(self.datasets.c.user_id == user_id)
        )
        self.session.commit()
        print(f"Delete operation took {time.time() - start_time} seconds")

    @cached(cache)
    def get_dataset_by_id(self, dataset_id, user_id):
        """
        Get a dataset by its ID, ensuring it's owned by the specified user.
        """
        start_time = time.time()
        result = self.session.execute(
            self.datasets.select().where(self.datasets.c.id == dataset_id).where(self.datasets.c.user_id == user_id)
        ).fetchone()
        print(f"Get operation took {time.time() - start_time} seconds")
        return result

    def update_last_accessed(self, dataset_id, user_id):
        """
        Update the last accessed time of a dataset, ensuring it's owned by the specified user.
        """
        start_time = time.time()
        self.session.execute(
            self.datasets.update().where(self.datasets.c.id == dataset_id).where(self.datasets.c.user_id == user_id).values(
                last_accessed=datetime.datetime.utcnow()
            )
        )
        self.session.commit()
        print(f"Update operation took {time.time() - start_time} seconds")

    def rename_dataset(self, dataset_id, new_name, user_id):
        """
        Rename a dataset, ensuring it's owned by the specified user.
        """
        start_time = time.time()
        self.session.execute(
            self.datasets.update().where(self.datasets.c.id == dataset_id).where(self.datasets.c.user_id == user_id).values(name=new_name)
        )
        self.session.commit()
        print(f"Rename operation took {time.time() - start_time} seconds")

    def dataset_exists(self, file_name, user_id):
        """
        Check if a dataset with the specified name exists for the specified user.
        """
        start_time = time.time()
        result = self.session.execute(
            self.datasets.select().where(self.datasets.c.name == file_name).where(self.datasets.c.user_id == user_id)
        ).fetchone()
        print(f"Exist check operation took {time.time() - start_time} seconds")
        return result is not None

    @staticmethod
    def try_parsing_csv(uploaded_file):
        """
        Attempt to parse the uploaded file as CSV.
        """
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
        """
        Attempt to parse the uploaded file as JSON.
        """
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
        """
        Close the session for the database connection.
        """
        cls.session.remove()

Dataset.close_session()
