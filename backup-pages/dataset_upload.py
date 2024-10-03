import streamlit as st
import pandas as pd
import io
import datetime
import json
from database import Dataset

dataset_db = Dataset()

def load_css():
    with open('static/style.css') as f:
        css_code = f.read()
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

def add_preloader():
    preloader_html = """
    <div id="preloader">
        <div id="loader"></div>
    </div>
    <script type="text/javascript">
    document.onreadystatechange = function () {
        if (document.readyState !== "complete") {
            document.querySelector(
            "body").style.visibility = "hidden";
            document.querySelector(
            "#preloader").style.visibility = "visible";
        } else {
            document.querySelector(
            "#preloader").style.display = "none";
            document.querySelector(
            "body").style.visibility = "visible";
        }
    };
    </script>
    """
    st.markdown(preloader_html, unsafe_allow_html=True)

def dataset_upload_page():
    load_css()
    add_preloader()
    st.header('Upload your dataset', divider='violet')

    with st.container(border=True):
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "json"])

        if uploaded_file is not None:
            file_name = uploaded_file.name
            file_format = file_name.split('.')[-1]
            file_size = uploaded_file.size
            data = uploaded_file.getvalue()

            if dataset_db.dataset_exists(file_name):
                st.warning("Dataset already exists.")
            else:
                try:
                    with st.spinner("Loading..."):
                        progress_text = st.empty()
                        progress_bar = st.progress(0)
                        for percent_complete in range(0, 101, 10):
                            progress_bar.progress(percent_complete)
                            progress_text.text(f"{percent_complete}%")

                        if file_format == 'csv':
                            df = Dataset.try_parsing_csv(io.BytesIO(data))
                            if df is None:
                                st.error("Failed to parse the CSV file. Please check the file format.")
                                return
                        elif file_format == 'xlsx':
                            import openpyxl
                            df = pd.read_excel(io.BytesIO(data), engine='openpyxl')
                        elif file_format == 'json':
                            df = Dataset.try_parsing_json(uploaded_file)
                            if df is None:
                                st.error("Failed to parse the JSON file. Please check the file format.")
                                return
                        else:
                            st.error("Unsupported file type")
                            return

                        if df.empty or df.columns.empty:
                            st.warning("The uploaded file is empty or does not contain any columns.")
                            return

                        st.session_state.df = df
                        st.session_state.dataset_name = file_name
                        dataset_db.save_to_database(file_name, file_format, file_size, data)
                        st.success("Dataset uploaded successfully!")
                        st.session_state.uploaded = True

                except pd.errors.ParserError as e:
                    st.error(f"Error parsing the file: {e}")
                    return
                except json.JSONDecodeError as e:
                    st.error(f"Error decoding JSON: {e}")
                    return
                except Exception as e:
                    st.error(f"Error reading the file: {e}")
                    return

        if st.session_state.get('uploaded'):
            if st.button("View Data Summary"):
                st.switch_page("pages/dataset_summary.py")

    datasets_list = dataset_db.fetch_datasets()

    if datasets_list:
        with st.container(border=True):
            st.write("### Recently Uploaded Datasets")
            search_query = st.text_input("Search Datasets", placeholder="Search...", help="Enter keywords to search for datasets")

            col1, col2, col3 = st.columns(3)
            with col1:
                filter_format = st.selectbox("Filter by Format", ["All", "csv", "xlsx", "json"])

            with col2:
                max_size = st.slider("Filter by Max Size (MB)", 0, 200, 200)
            with col3:
                filter_date = st.date_input("Filter by Date", value=(datetime.date(2024, 1, 1), datetime.date.today()), key="date_filter")

        with st.container(border=True):
            st.write('<div class="recent-files">', unsafe_allow_html=True)
            # st.write('<div class="recent-file-header">', unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns([7, 3, 3, 4, 3])
            with col1:
                st.write("**Name**")
            with col2:
                st.write("**Format**")
            with col3:
                st.write("**Size**")
            with col4:
                st.write("**Date & Time**")
            with col5:
                st.write("**Action**")
            st.write('</div>', unsafe_allow_html=True)

            # Ensure filter_date is a tuple with two dates
            if isinstance(filter_date, tuple) and len(filter_date) == 2:
                start_date, end_date = filter_date
            else:
                start_date, end_date = datetime.date(2024, 1, 1), datetime.date.today()

            filtered_datasets = [
                ds for ds in datasets_list 
                if search_query.lower() in ds.name.lower() and 
                (filter_format == "All" or ds.file_format == filter_format) and 
                (ds.file_size <= max_size * 1024 * 1024) and 
                (start_date <= ds.upload_date.date() <= end_date)
            ]

            for ds in filtered_datasets:
                st.write('<div class="recent-file-item">', unsafe_allow_html=True)
                col1, col2, col3, col4, col5 = st.columns([7, 3, 3, 4, 3])
                with col1:
                    dataset_name = ds.name.split('.')[0]
                    if st.button(f"{dataset_name}", key=f"view_{ds.id}"):
                        view_dataset_summary(ds.id)
                with col2:
                    st.write(f"{ds.file_format.upper()}")
                with col3:
                    st.write(f"{round(ds.file_size / (1024 * 1024), 2)} MB")
                with col4:
                    st.write(f"{ds.upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
                with col5:
                    if st.button("Delete", key=f"delete_{ds.id}"):
                        delete_dataset(ds.id)
                st.write('</div>', unsafe_allow_html=True)
            st.write('</div>', unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.write("You don't have any datasets uploaded. Please upload a dataset to get started.")

def view_dataset_summary(dataset_id):
    dataset = dataset_db.get_dataset_by_id(dataset_id)
    if dataset:
        data = dataset.data
        file_format = dataset.file_format
        if file_format == 'csv':
            df = Dataset.try_parsing_csv(io.BytesIO(data))
        elif file_format == 'xlsx':
            df = pd.read_excel(io.BytesIO(data), engine='openpyxl')
        elif file_format == 'json':
            try:
                data_str = data.decode('utf-8').strip().split('\n')
                json_data = [json.loads(line) for line in data_str if line.strip()]
                df = pd.json_normalize(json_data)
            except json.JSONDecodeError as e:
                st.error(f"Error parsing the JSON file: {e}")
                return
        st.session_state.df = df
        st.session_state.dataset_name = dataset.name
        st.switch_page("pages/dataset_summary.py")

def delete_dataset(dataset_id):
    dataset_db.delete_dataset(dataset_id)
    st.experimental_rerun()

dataset_upload_page()
