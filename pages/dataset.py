import streamlit as st
import pandas as pd
import io
import datetime
from dataset import Dataset
from kaggle.api.kaggle_api_extended import KaggleApi
import os
import tempfile
import requests
import shutil
import zipfile

def load_css():
    """Load custom CSS to style the interface."""
    try:
        css_path = os.path.join(os.path.dirname(__file__), "../static/style.css")
        with open(css_path) as f:
            css_code = f.read()
        st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS file not found. Using default styles.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

                
with st.spinner("Loading Please Wait ..."):
    
    with st.container(border=True):
    
        st.header('Dataset')
        st.write('Effortlessly manage your datasets with tools for seamless uploads and powerful searches.')
        datasetupload_tab, datasetsearch_tab = st.tabs([
            "⬆️ Dataset Upload",
            "🔎 Dataset Search"
        ])
    
        with datasetupload_tab:
    
            class DatasetUploadManager:
                def __init__(self):
                    self.dataset_db = Dataset()    
            
                def categorize_by_time(self, datasets):
                    today = datetime.datetime.now().date()
                    yesterday = today - datetime.timedelta(days=1)
                    last_7_days = today - datetime.timedelta(days=7)
                    last_30_days = today - datetime.timedelta(days=30)
            
                    categorized = {
                        "Today": [],
                        "Yesterday": [],
                        "Previous 7 days": [],
                        "Previous 30 days": [],
                        "Older": []
                    }
            
                    for ds in datasets:
                        last_accessed_date = ds.last_accessed.date()
                        if last_accessed_date == today:
                            categorized["Today"].append(ds)
                        elif last_accessed_date == yesterday:
                            categorized["Yesterday"].append(ds)
                        elif last_accessed_date > last_7_days:
                            categorized["Previous 7 days"].append(ds)
                        elif last_accessed_date > last_30_days:
                            categorized["Previous 30 days"].append(ds)
                        else:
                            categorized["Older"].append(ds)
            
                    return categorized
            
    
                def format_file_size(self, file_size_bytes):
                    """Helper function to display file size in KB or MB"""
                    if file_size_bytes < 1024 * 1024:
                        return f"{round(file_size_bytes / 1024, 2)} KB"
                    else:
                        return f"{round(file_size_bytes / (1024 * 1024), 2)} MB"
    
            
                def get_column_and_row_count(self, dataset):
                    """Load the dataset and calculate the column and row count."""
                    data = dataset.data
                    file_format = dataset.file_format
                    try:
                        if file_format == 'csv':
                            df = Dataset.try_parsing_csv(io.BytesIO(data))
                        elif file_format == 'xlsx': 
                            df = pd.read_excel(io.BytesIO(data), engine='openpyxl') 
                        else:
                            return None, None
                
                        return len(df.columns), len(df)
                    except Exception:
                        return None, None
    
    
                def dataset_upload_page(self):
                    load_css()
                    st.write('##### Upload your dataset')
                
                    if 'user_id' not in st.session_state or not st.session_state['user_id']:
                        st.error("Please log in to upload and view your datasets.")
                        return
                
                    user_id = st.session_state['user_id']
                
                    if 'uploaded' not in st.session_state:
                        st.session_state.uploaded = False
                    if 'show_summary_button' not in st.session_state:
                        st.session_state.show_summary_button = False
                    if 'rename_action_state' not in st.session_state:
                        st.session_state.rename_action_state = {}
                
                    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"], key="uploaded_file")
    
                    if uploaded_file is not None:
                        file_name = uploaded_file.name
                        file_format = file_name.split('.')[-1]
                        file_size = uploaded_file.size
                        data = uploaded_file.getvalue()
                
                        if file_size > 200 * 1024 * 1024:  
                            st.error("The file exceeds the 200MB size limit.")
                            return
                
                        if self.dataset_db.dataset_exists(file_name, user_id):
                            st.warning("Dataset with this name already exists.")
                        else:
                            try:
                                with st.spinner("Loading..."):
                                    if file_format == 'csv':
                                        df = Dataset.try_parsing_csv(io.BytesIO(data))
                                        if df is None:
                                            st.error("Failed to parse the CSV file. Please check the file format.")
                                            return
                                    elif file_format == 'xlsx': 
                                        df = pd.read_excel(io.BytesIO(data), engine='openpyxl')
                                    else:
                                        st.error("Unsupported file type")
                                        return
                
                                    if df is None or df.empty or df.columns.empty:
                                        st.warning("The uploaded file is empty or does not contain any columns.")
                                        return
                
                                    st.session_state.df = df
                                    st.session_state.dataset_name = file_name
                                    self.dataset_db.save_to_database(file_name, file_format, file_size, data, user_id)
                                    st.success("Dataset uploaded successfully!")
                                    st.session_state.uploaded = True
                                    st.session_state.show_summary_button = True
                
                            except Exception as e:
                                st.error(f"Error reading the file: {e}")
                                return
                
                    st.markdown('') 
                    st.markdown('') 
                
                    datasets_list = self.dataset_db.fetch_datasets(user_id)
                
                    if datasets_list:
                        show_filter = st.checkbox("Show Filter Options", value=False)
                
                        if show_filter:
                            col_filter, _, col_data = st.columns([0.17, 0.03, 0.83]) 
                        else:
                            _, col_data = st.columns([0.01, 1.0])  
                
                        if show_filter:
                            with col_filter:
                                st.write("##### Filter Options")
                                search_query = st.text_input("Search Datasets", placeholder="Search...", help="Enter keywords to search for datasets")
                                filter_format = st.selectbox("Filter by Format", ["All", "csv", "xlsx"])
                                min_size, max_size = st.slider("File Size Range (MB)", 0, 200, (0, 200), help="Select the minimum and maximum file sizes")
                                filter_date_range = st.date_input("Date Range", value=(datetime.date(2024, 1, 1), datetime.date.today()), key="date_range_filter")
                                last_accessed_filter = st.selectbox("Last Accessed", ["All", "Today", "Yesterday", "Last 7 Days", "Last 30 Days"])
                                min_columns, max_columns = st.slider("Column Count Range", 0, 100, (0, 100), help="Select the minimum and maximum number of columns")
                                min_rows, max_rows = st.slider("Row Count Range", 0, 100000, (0, 100000), help="Select the minimum and maximum number of rows")
                
                        if not show_filter:
                            search_query = ""
                            filter_format = "All"
                            min_size, max_size = 0, 200
                            filter_date_range = (datetime.date(2024, 1, 1), datetime.date.today())
                            last_accessed_filter = "All"
                            min_columns, max_columns = 0, 100
                            min_rows, max_rows = 0, 100000
                
                        with col_data:
                            st.write("##### Recently Uploaded Datasets")
                            with st.spinner("Loading dataset..."):
                
                                if isinstance(filter_date_range, tuple) and len(filter_date_range) == 2:
                                    start_date, end_date = filter_date_range
                                else:
                                    start_date, end_date = datetime.date(2024, 1, 1), datetime.date.today()
                
                                filtered_datasets = [
                                    ds for ds in datasets_list
                                    if search_query.lower() in ds.name.lower() and
                                    (filter_format == "All" or ds.file_format == filter_format) and
                                    (min_size * 1024 * 1024 <= ds.file_size <= max_size * 1024 * 1024) and
                                    (start_date <= ds.last_accessed.date() <= end_date) and
                                    (
                                        last_accessed_filter == "All" or
                                        (last_accessed_filter == "Today" and ds.last_accessed.date() == datetime.datetime.now().date()) or
                                        (last_accessed_filter == "Yesterday" and ds.last_accessed.date() == datetime.datetime.now().date() - datetime.timedelta(days=1)) or
                                        (last_accessed_filter == "Last 7 Days" and ds.last_accessed.date() >= datetime.datetime.now().date() - datetime.timedelta(days=7)) or
                                        (last_accessed_filter == "Last 30 Days" and ds.last_accessed.date() >= datetime.datetime.now().date() - datetime.timedelta(days=30))
                                    )
                                ]
                
                                final_filtered_datasets = []
                                for ds in filtered_datasets:
                                    col_count, row_count = self.get_column_and_row_count(ds)
                                    if col_count is not None and row_count is not None:
                                        if min_columns <= col_count <= max_columns and min_rows <= row_count <= max_rows:
                                            final_filtered_datasets.append(ds)
                
                                final_filtered_datasets.sort(key=lambda x: x.last_accessed, reverse=True)
                                categorized_datasets = self.categorize_by_time(final_filtered_datasets)
                
                                for category, datasets in categorized_datasets.items():
                                    if datasets:
                                        st.write(f"###### {category}")
                                        for ds in datasets:                                         
    
                                            col1, col2, col3, col4, col5 = st.columns([0.55, 0.08, 0.08, 0.17, 0.15])
    
                                            with col1:
                                                dataset_name = ds.name.split('.')[0]
                                                st.write(f"{dataset_name}")
                                                
                                            with col2:
                                                st.write(f"{ds.file_format.upper()}")
    
                                            with col3:
                                                st.write(f"{self.format_file_size(ds.file_size)}")
    
                                            with col4:
                                                st.write(f"{ds.last_accessed.strftime('%Y-%m-%d %H:%M:%S')}")
    
                                            with col5:
                                                
                                                action_key = f"action_{ds.id}"
                                                action = st.selectbox(
                                                    " ",
                                                    ["Select", "View Summary", "Preprocessing", "Visualization", "Chat", "Models", "Delete"],
                                                    key=action_key,
                                                    index=st.session_state.rename_action_state.get(ds.id, 0)
                                                )
                
                                                if action == "View Summary":
                                                    self.view_dataset_summary(ds.id)
                
                                                elif action == "Preprocessing":
                                                    dataset = self.dataset_db.get_dataset_by_id(ds.id, user_id)
                                                    st.session_state.df_to_preprocess = dataset.data
                                                    st.session_state.dataset_name_to_preprocess = dataset.name
                                                    st.session_state.dataset_id_to_preprocess = ds.id
                                                    st.switch_page("pages/data_preprocessing.py")
                
                                                elif action == "Visualization":
                                                    dataset = self.dataset_db.get_dataset_by_id(ds.id, user_id)
                                                    st.session_state.df_to_visualize = dataset.data
                                                    st.session_state.dataset_name_to_visualize = dataset.name
                                                    st.switch_page("pages/data_visualization.py")
                
                                                elif action == "Chat":
                                                    dataset = self.dataset_db.get_dataset_by_id(ds.id, user_id)
                                                    st.session_state.df_to_chat = dataset.data
                                                    st.session_state.dataset_name_to_chat = dataset.name
                                                    st.session_state['chat_history'] = []
                                                    st.switch_page("pages/chatbot.py")
                                                elif action == "Models":
                                                    from pages.models import reset_results_on_new_dataset
                                                    reset_results_on_new_dataset()
                                                    dataset = self.dataset_db.get_dataset_by_id(ds.id, user_id)
                                                    st.session_state.df_for_modeling = dataset.data
                                                    st.session_state.dataset_name_for_modeling = dataset.name
                                                    st.switch_page("pages/models.py")
                
                                                elif action == "Delete":
                                                    self.delete_dataset(ds.id)
                
                                            st.write("---")
                
                                if not final_filtered_datasets:
                                    st.write("You don't have any datasets matching the selected filters.")
                
                    else:
                        st.write("You don't have any datasets uploaded. Please upload a dataset to get started.")
            
    
                def view_dataset_summary(self, dataset_id):
                    user_id = st.session_state['user_id']  
                    dataset = self.dataset_db.get_dataset_by_id(dataset_id, user_id)
                    if dataset:
                        data = dataset.data
                        file_format = dataset.file_format
                        if file_format == 'csv':
                            df = Dataset.try_parsing_csv(io.BytesIO(data))
                            if df is None:
                                st.error("Failed to parse the CSV file. Please check the file format.")
                                return
                        elif file_format == 'xlsx':  
                            df = pd.read_excel(io.BytesIO(data), engine='openpyxl')
                            if df is None:
                                st.error("Failed to parse the Excel file. Please check the file format.")
                                return
                        else:
                            st.error("Unsupported file type")
                            return
    
                        st.session_state.df = df
                        st.session_state.dataset_name = dataset.name
                        st.session_state.dataset_id = dataset_id
                        self.dataset_db.update_last_accessed(dataset_id, user_id)
                        st.switch_page("pages/dataset_summary.py")
                        
    
                def delete_dataset(self, dataset_id):
                    user_id = st.session_state['user_id']  
                    self.dataset_db.delete_dataset(dataset_id, user_id)
                    st.rerun()
        
            manager = DatasetUploadManager()
            manager.dataset_upload_page()
        
    
        with datasetsearch_tab:
        
            class DatasetSearch:
                def __init__(self):
                    import os
            
                    # Load Kaggle credentials
                    os.environ['KAGGLE_USERNAME'] = "hoorainhabibabbasi"
                    os.environ['KAGGLE_KEY'] = "c6267653dad344a650deac0efd9f6e50"
            
                    # Debug environment variable loading
                    print("KAGGLE_USERNAME:", os.environ.get('KAGGLE_USERNAME'))
                    print("KAGGLE_KEY:", os.environ.get('KAGGLE_KEY'))
            
                    try:
                        self.kaggle_api = KaggleApi()
                        self.kaggle_api.authenticate()
                    except IOError as e:
                        st.error(f"Error authenticating with Kaggle API: {e}")
            
                def dataset_search_page(self):
                    self.load_css()
                    st.write("##### Search Options")
            
                    source_option = st.radio("Choose a data source", ["Kaggle", "Data.gov"], index=0)
            
                    search_query = st.text_input("Search Datasets", placeholder="Search datasets...", help="Enter keywords to search for datasets.")
            
                    if search_query:
                        st.write("##### Search Results")
                        with st.spinner("Searching..."):
                            if source_option == "Kaggle":
                                kaggle_datasets = self.search_kaggle_datasets(search_query)
                                self.display_datasets(kaggle_datasets, source='Kaggle')
                            elif source_option == "Data.gov":
                                data_gov_datasets = self.search_data_gov_datasets(search_query)
                                self.display_datasets(data_gov_datasets, source='Data.gov')
                    else:
                        st.write("Enter a search query to find datasets.")
            
                def load_css(self):
                    # Add your custom CSS here if needed
                    pass
            
                def search_kaggle_datasets(self, query):
                    datasets = self.kaggle_api.dataset_list(search=query)
                    results = []
                    for ds in datasets:
                        results.append({
                            'id': ds.ref,
                            'title': ds.title,
                            'size': round(ds.totalBytes / (1024 * 1024), 2), 
                            'lastUpdated': ds.lastUpdated
                        })
                    return results
            
                def search_data_gov_datasets(self, query):
                    url = "https://catalog.data.gov/api/3/action/package_search"
                    params = {
                        "q": query,
                        "rows": 10
                    }
                
                    response = requests.get(url, params=params)
                
                    if response.status_code == 200:
                        try:
                            datasets = response.json().get('result', {}).get('results', [])
                            results = []
                            for ds in datasets:
                                resources = ds.get('resources', [])
                                download_urls = []
                
                                # Collect all available formats, even if unsupported
                                for res in resources:
                                    format_type = res.get('format', 'Unknown').upper()
                                    url = res.get('url', 'No URL available')
                                    download_urls.append((format_type, url))
                
                                last_updated = ds.get('metadata_modified', 'N/A')
                                formatted_last_updated = last_updated[:10]  # Format as YYYY-MM-DD
                
                                results.append({
                                    'id': ds.get('id', 'N/A'),
                                    'title': ds.get('title', 'N/A'),
                                    'lastUpdated': formatted_last_updated,
                                    'download_urls': download_urls  # Include all resources with formats
                                })
                            return results
                        except ValueError as e:
                            st.error(f"Error parsing JSON response: {e}")
                            return []
                    else:
                        st.error(f"Error fetching Data.gov datasets: {response.status_code} - {response.text}")
                        return []
                
            
                def display_datasets(self, datasets, source):
                    if datasets:
                        st.write('<div class="recent-file-item">', unsafe_allow_html=True)
                        col1, col2, col3, col4 = st.columns([5, 2, 3, 3])
                        with col1:
                            st.write("**Name**")
                        if source == 'Kaggle':
                            with col2:
                                st.write("**Size (MB)**")
                        with col3:
                            st.write("**Date**")
                        with col4:
                            st.write("**Action**")
                        st.write('</div>', unsafe_allow_html=True)
            
                        for idx, ds in enumerate(datasets):
                            st.write('<div class="recent-file-item">', unsafe_allow_html=True)
                            col1, col2, col3, col4 = st.columns([5, 2, 3, 3])
                            with col1:
                                st.write(ds['title'])
                            if source == 'Kaggle':
                                with col2:
                                    st.write(ds['size'])
                            with col3:
                                st.write(ds.get('lastUpdated', 'N/A'))
                            with col4:
                                if source == 'Kaggle':
                                    download_link = self.create_download_link(ds['id'])
                                    if download_link:
                                        st.download_button(
                                            label="Download", 
                                            data=download_link['data'], 
                                            file_name=download_link['file_name'], 
                                            mime=download_link['mime'],
                                            key=f"kaggle_download_{idx}"  # Unique key for each button
                                        )
                                elif source == 'Data.gov':
                                    if ds['download_urls']:
                                        selected_format = st.selectbox(
                                            f"Select format for {ds['title']}",
                                            options=[fmt for fmt, url in ds['download_urls']],
                                            key=f"selectbox_{ds['id']}"  # Unique key for each selectbox
                                        )
                                        download_url = next(url for fmt, url in ds['download_urls'] if fmt == selected_format)
            
                                        if selected_format == "JSON":
                                            response = requests.get(download_url)
                                            if response.status_code == 200:
                                                try:
                                                    json_data = response.json()
                                                    json_str = json.dumps(json_data, indent=4)
                                                    st.download_button(
                                                        label="Download JSON", 
                                                        data=json_str, 
                                                        file_name=f"{ds['title']}.json", 
                                                        mime="application/json",
                                                        key=f"json_download_{ds['id']}"  # Unique key for each button
                                                    )
                                                except json.JSONDecodeError:
                                                    st.error("Invalid JSON file format.")
                                            else:
                                                st.error(f"Failed to download JSON file: {response.status_code}")
                                        else:
                                            st.download_button(
                                                label="Download",
                                                data=download_url,
                                                file_name=f"{ds['title']}.{selected_format.lower()}",
                                                key=f"datagov_download_{ds['id']}"  # Unique key for each button
                                            )
                                    else:
                                        st.write("No formats available.")
                            st.write('</div>', unsafe_allow_html=True)
                    else:
                        st.write("No datasets found.")
            

                def create_download_link(self, dataset_ref):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Download the dataset files into a temporary directory
                        self.kaggle_api.dataset_download_files(dataset_ref, path=temp_dir, unzip=True)
                
                        # Check if the downloaded content is a single file or multiple files in a directory
                        files = os.listdir(temp_dir)
                
                        if len(files) == 1:  # If there's only one file, return its content
                            file_path = os.path.join(temp_dir, files[0])
                            if os.path.isfile(file_path):  # Ensure it's a file, not a directory
                                with open(file_path, 'rb') as f:
                                    file_data = f.read()
                
                                return {
                                    "data": file_data,
                                    "file_name": files[0],
                                    "mime": "application/octet-stream"
                                }
                            else:
                                st.error("Expected a file but found a directory.")
                        elif len(files) > 1:  # If there are multiple files, zip them
                            zip_file_path = os.path.join(temp_dir, f"{dataset_ref.replace('/', '_')}.zip")
                            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                                for file_name in files:
                                    file_path = os.path.join(temp_dir, file_name)
                                    zipf.write(file_path, arcname=file_name)
                
                            with open(zip_file_path, 'rb') as f:
                                zip_data = f.read()
                
                            return {
                                "data": zip_data,
                                "file_name": f"{dataset_ref.replace('/', '_')}.zip",
                                "mime": "application/zip"
                            }
                        else:
                            st.error("No files were found in the dataset.")
                            return None
                
            
            search_app = DatasetSearch()
            search_app.dataset_search_page()
            
