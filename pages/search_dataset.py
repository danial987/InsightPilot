import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi
import os
import tempfile
import requests
import json

class DatasetSearch:
    def __init__(self):
        os.environ['KAGGLE_USERNAME'] = "hoorainhabibabbasi" 
        os.environ['KAGGLE_KEY'] = "c6267653dad344a650deac0efd9f6e50"  

        self.kaggle_api = KaggleApi()
        self.kaggle_api.authenticate()

    def load_css(self):
        with open('static/style.css') as f:
            css_code = f.read()
        st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

    def dataset_search_page(self):
        self.load_css()
        st.header('Search Datasets', divider='violet')

        with st.container(border=True):
            source_option = st.radio("Choose a data source", ["Kaggle", "Data.gov"], index=0)
        with st.container(border=True):
            search_query = st.text_input("Search Datasets", placeholder="Search datasets...", help="Enter keywords to search for datasets.")
            if search_query:
                if source_option == "Kaggle":
                    kaggle_datasets = self.search_kaggle_datasets(search_query)
                    self.display_datasets(kaggle_datasets, source='Kaggle')
                elif source_option == "Data.gov":
                    data_gov_datasets = self.search_data_gov_datasets(search_query)
                    self.display_datasets(data_gov_datasets, source='Data.gov')
            else:
                st.write("Enter a search query to find datasets.")

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

                    allowed_formats = ['CSV', 'JSON', 'XLSX']
                    filtered_resources = [
                        res for res in resources if res['format'].upper() in allowed_formats
                    ]

                    for res in filtered_resources:
                        format_type = res['format'].upper()
                        if format_type not in [fmt for fmt, url in download_urls]:
                            download_urls.append((format_type, res.get('url', 'No direct download available.')))

                    last_updated = ds.get('metadata_modified', 'N/A')
                    formatted_last_updated = last_updated[:10] 

                    results.append({
                        'id': ds.get('id', 'N/A'),
                        'title': ds.get('title', 'N/A'),
                        'lastUpdated': formatted_last_updated,  
                        'download_urls': download_urls 
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
                        download_link = self.create_download_link(ds['id'])
                        if download_link:
                            st.download_button(label="Download", 
                                               data=download_link['data'], 
                                               file_name=download_link['file_name'], 
                                               mime=download_link['mime'])
                    elif source == 'Data.gov':
                        if ds['download_urls']:
                            selected_format = st.selectbox(
                                f"Select format for {ds['title']}",
                                options=[fmt for fmt, url in ds['download_urls']],
                                key=f"{ds['id']}_selectbox" 
                            )
                            download_url = next(url for fmt, url in ds['download_urls'] if fmt == selected_format)
                            
                            if selected_format == "JSON":
                                response = requests.get(download_url)
                                if response.status_code == 200:
                                    try:
                                        json_data = response.json() 
                                        json_str = json.dumps(json_data, indent=4)  
                                        st.download_button(label="Download JSON", data=json_str, file_name=f"{ds['title']}.json", mime="application/json")
                                    except json.JSONDecodeError:
                                        st.error("Invalid JSON file format.")
                                else:
                                    st.error(f"Failed to download JSON file: {response.status_code}")
                            else:
                                st.download_button(label="Download", data=download_url, file_name=f"{ds['title']}.{selected_format.lower()}")
                        else:
                            st.write("No formats available.")
                st.write('</div>', unsafe_allow_html=True)
        else:
            st.write("No datasets found.")

    def create_download_link(self, dataset_ref):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.kaggle_api.dataset_download_files(dataset_ref, path=temp_dir, unzip=True) 
            files = os.listdir(temp_dir) 

            if files:
                original_file = files[0]
                file_path = os.path.join(temp_dir, original_file)

                with open(file_path, 'rb') as f:
                    file_data = f.read()

                return {
                    "data": file_data,
                    "file_name": original_file,  
                    "mime": "application/octet-stream"
                }

        st.error("No files found for download.")
        return None

search_app = DatasetSearch()
search_app.dataset_search_page()