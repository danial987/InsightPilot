import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi
import os
import tempfile
import requests

# Set Kaggle credentials programmatically
os.environ['KAGGLE_USERNAME'] = "hoorainhabibabbasi"  # Your Kaggle username
os.environ['KAGGLE_KEY'] = "c6267653dad344a650deac0efd9f6e50"  # Your Kaggle API key

# Initialize Kaggle API and authenticate
kaggle_api = KaggleApi()
kaggle_api.authenticate()

def load_css():
    with open('static/style.css') as f:
        css_code = f.read()
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

def dataset_search_page():
    load_css()
    st.header('Search Datasets', divider='violet')

    with st.container(border=True):
        source_option = st.radio("Choose a data source", ["Kaggle", "Data.gov"], index=0)
    with st.container(border=True):
        search_query = st.text_input("Search Datasets", placeholder="Search datasets...", help="Enter keywords to search for datasets.")
        if search_query:
            if source_option == "Kaggle":
                kaggle_datasets = search_kaggle_datasets(search_query)
                display_datasets(kaggle_datasets, source='Kaggle')
            elif source_option == "Data.gov":
                data_gov_datasets = search_data_gov_datasets(search_query)
                display_datasets(data_gov_datasets, source='Data.gov')
        else:
            st.write("Enter a search query to find datasets.")

def search_kaggle_datasets(query):
    datasets = kaggle_api.dataset_list(search=query)
    results = []
    for ds in datasets:
        results.append({
            'id': ds.ref,
            'title': ds.title,
            'size': round(ds.totalBytes / (1024 * 1024), 2),  # Convert to MB
            'lastUpdated': ds.lastUpdated
        })
    return results

def search_data_gov_datasets(query):
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

                # Filter resources for allowed formats (CSV, JSON, XLSX)
                allowed_formats = ['CSV', 'JSON', 'XLSX']
                filtered_resources = [
                    res for res in resources if res['format'].upper() in allowed_formats
                ]

                # Create download URLs for each filtered resource
                for res in filtered_resources:
                    format_type = res['format'].upper()
                    if format_type not in [fmt for fmt, url in download_urls]:
                        download_urls.append((format_type, res.get('url', 'No direct download available.')))

                # Format the last updated date similarly to Kaggle
                last_updated = ds.get('metadata_modified', 'N/A')
                formatted_last_updated = last_updated[:10]  # Get only the date part (YYYY-MM-DD)

                results.append({
                    'id': ds.get('id', 'N/A'),
                    'title': ds.get('title', 'N/A'),
                    'lastUpdated': formatted_last_updated,  # Format the date
                    'download_urls': download_urls  # Store download URLs
                })
            return results
        except ValueError as e:
            st.error(f"Error parsing JSON response: {e}")
            return []
    else:
        st.error(f"Error fetching Data.gov datasets: {response.status_code} - {response.text}")
        return []

def display_datasets(datasets, source):
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

        for ds in datasets:
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
                    # Combine both buttons into one for seamless download
                    download_link = create_download_link(ds['id'])
                    if download_link:
                        st.download_button(label="Download", 
                                           data=download_link['data'], 
                                           file_name=download_link['file_name'], 
                                           mime=download_link['mime'])
                elif source == 'Data.gov':
                    # Allow user to choose format
                    if ds['download_urls']:
                        selected_format = st.selectbox(
                            f"Select format for {ds['title']}",
                            options=[fmt for fmt, url in ds['download_urls']]
                        )
                        download_url = next(url for fmt, url in ds['download_urls'] if fmt == selected_format)
                        st.download_button(label="Download", data=download_url, file_name=f"{ds['title']}.{selected_format.lower()}", help="Download")
                    else:
                        st.write("No formats.")
            st.write('</div>', unsafe_allow_html=True)
    else:
        st.write("No datasets found.")

def create_download_link(dataset_ref):
    # Prepare to download the original files instead of zipping
    with tempfile.TemporaryDirectory() as temp_dir:
        kaggle_api.dataset_download_files(dataset_ref, path=temp_dir, unzip=True)  # Unzip files to temp_dir
        files = os.listdir(temp_dir)  # List all files in temp_dir

        # Check if files are present
        if files:
            # Use the first file found for download (assuming the dataset may contain multiple files)
            original_file = files[0]
            file_path = os.path.join(temp_dir, original_file)

            with open(file_path, 'rb') as f:
                file_data = f.read()

            return {
                "data": file_data,
                "file_name": original_file,  # Return original file name
                "mime": "application/octet-stream"  # Set a generic MIME type
            }

    st.error("No files found for download.")
    return None

# Call the dataset_search_page function in your app
dataset_search_page()
