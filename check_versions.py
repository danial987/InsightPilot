import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
import requests
import psycopg2
import sqlalchemy
import st_pages
import plotly

# Create a dictionary to store the library versions
versions = {
    "streamlit": st.__version__,
    "pandas": pd.__version__,
    "numpy": np.__version__,
    "openpyxl": openpyxl.__version__,
    "requests": requests.__version__,
    "psycopg2": psycopg2.__version__,
    "sqlalchemy": sqlalchemy.__version__,
    "st_pages": st_pages.__version__,
    "plotly": plotly.__version__,
}

# Display the versions
for library, version in versions.items():
    st.write(f"{library}: {version}")
