import streamlit as st
import pandas as pd
import numpy as np
import yaml
from streamlit_pandas_profiling import st_profile_report
from ydata_profiling import ProfileReport
from ydata_profiling.config import Settings

def load_css():
    with open('static/style.css') as f:
        css_code = f.read()
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return Settings(**config)

class DatasetSummary:
    @staticmethod
    def display_summary(df, dataset_name):
        st.write(f"### Dataset: {dataset_name}")

        with st.container(border=True, height=100):
            st.write(f"Number of Rows: {df.shape[0]}")
            st.write(f"Number of Columns: {df.shape[1]}")

        with st.container(border=True):
            st.write("### Feature Names")
            st.write(df.columns.tolist())

        col1, col2 = st.columns(2)
        with col1:
            container = st.container(border=True, height=400)
            with container:
                st.write("### Categorical Features:")
                categorical_features = df.select_dtypes(include=['object']).columns.tolist()
                st.write(categorical_features)
        with col2:
            container = st.container(border=True, height=400)
            with container:
                st.write("### Numerical Features:")
                numerical_features = df.select_dtypes(include=[np.number]).columns.tolist()
                st.write(numerical_features)

        with st.container(border=True):
            if st.button("View Data Types", key="view_data_types"):
                st.session_state.show_data_types = not st.session_state.get('show_data_types', False)
            if st.session_state.get('show_data_types', False):
                st.subheader("Data Types")
                st.write(df.dtypes)

        with st.container(border=True):
            if st.button("View Distinct Values for Categorical Features", key="view_distinct_values"):
                st.session_state.show_distinct_values = not st.session_state.get('show_distinct_values', False)
            if st.session_state.get('show_distinct_values', False):
                st.subheader("Distinct Values for Categorical Features")
                for feature in categorical_features:
                    try:
                        distinct_count = df[feature].apply(lambda x: str(x)).nunique()
                        st.write(f"**{feature}**: {distinct_count} distinct values")
                    except TypeError:
                        st.write(f"**{feature}**: Unable to determine distinct values due to unhashable data type")

        with st.container(border=True):
            if st.button("View Basic Statistics for Numerical Columns", key="view_basic_statistics"):
                st.session_state.show_basic_statistics = not st.session_state.get('show_basic_statistics', False)
            if st.session_state.get('show_basic_statistics', False):
                st.subheader("Basic Statistics for Numerical Columns")
                if not df.empty:
                    st.write(df.describe())
                else:
                    st.write("No numerical columns found or DataFrame is empty.")

        with st.container(border=True):
            tab1, tab2, tab3 = st.tabs(["Dataset Head", "Dataset Middle", "Dataset Footer"])
            with tab1:
                st.write("### Dataset Head")
                st.write(df.head())
            with tab2:
                st.write("### Dataset Middle")
                st.write(df.iloc[len(df)//2:len(df)//2+5])
            with tab3:
                st.write("### Dataset Footer")
                st.write(df.tail())

        with st.container(border=True):
            st.write("### Full DataFrame")
            st.dataframe(df)

        with st.container(border=True):
            if st.button("Generate Dataset Report", key="generate_profile_report"):
                st.session_state.show_profile_report = not st.session_state.get('show_profile_report', False)
            if st.session_state.get('show_profile_report', False):
                # Take a sample of the data if it is too large
                if df.shape[0] > 20000:  # You can adjust this threshold
                    df_sample = df.sample(n=20000, random_state=1)
                    st.warning(f"Dataset is large. Generating dataset report on a sample of 20,000 rows.")
                else:
                    df_sample = df

                # Load configuration from the YAML file
                config_path = 'config_minimal.yaml'
                config = load_config(config_path)

                # Create the ProfileReport instance with the loaded configuration
                pr = ProfileReport(df_sample, config=config)
                st_profile_report(pr)

def dataset_summary_page():
    load_css()
    st.header('Dataset Summary', divider='violet')

    if 'df' in st.session_state and 'dataset_name' in st.session_state:
        df = st.session_state.df
        dataset_name = st.session_state.dataset_name

        if st.button("Back to Upload", key="back_to_upload"):
            st.session_state.uploaded = False
            st.switch_page("pages/dataset_upload.py")

        DatasetSummary.display_summary(df, dataset_name)

dataset_summary_page()
