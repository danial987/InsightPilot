import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi
import os
import zipfile
import tempfile

# Initialize Kaggle API and authenticate
kaggle_api = KaggleApi()
kaggle_api.authenticate()

def load_css():
    with open('static/style.css') as f:
        css_code = f.read()
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

def dataset_search_page():
    load_css()
    st.header('Search Kaggle Datasets', divider='violet')

    with st.container():
        st.write("### Search for Kaggle Datasets")
        search_query = st.text_input("Search Datasets", placeholder="Search Kaggle datasets...", help="Enter keywords to search for datasets on Kaggle.")

        if search_query:
            kaggle_datasets = search_kaggle_datasets(search_query)
            if kaggle_datasets:
                st.write('<div class="recent-file-item">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns([7, 3, 4, 3])
                with col1:
                    st.write("**Name**")
                with col2:
                    st.write("**Size**")
                with col3:
                    st.write("**Date & Time**")
                with col4:
                    st.write("**Action**")
                st.write('</div>', unsafe_allow_html=True)

                for ds in kaggle_datasets:
                    st.write('<div class="recent-file-item">', unsafe_allow_html=True)
                    col1, col2, col3, col4 = st.columns([7, 3, 4, 3])
                    with col1:
                        st.write(ds['title'])
                    with col2:
                        st.write(f"{ds['size']} MB")
                    with col3:
                        st.write(ds['lastUpdated'])
                    with col4:
                        download_button_placeholder = st.empty()
                        if download_button_placeholder.button("Download", key=f"download_{ds['id']}"):
                            with st.spinner('Preparing download...'):
                                download_link = create_download_link(ds['id'], ds['title'])
                                download_button_placeholder.download_button(label="Download", data=download_link['data'], file_name=download_link['file_name'], mime="application/zip")
                    st.write('</div>', unsafe_allow_html=True)
            else:
                st.write("No datasets found on Kaggle.")
        else:
            st.write("Enter a search query to find datasets on Kaggle.")

def search_kaggle_datasets(query):
    datasets = kaggle_api.dataset_list(search=query)
    results = []
    for ds in datasets:
        results.append({
            'id': ds.ref,
            'title': ds.title,
            'size': round(ds.totalBytes / (1024 * 1024), 2),
            'lastUpdated': ds.lastUpdated
        })
    return results

def create_download_link(dataset_ref, title):
    with tempfile.TemporaryDirectory() as temp_dir:
        kaggle_api.dataset_download_files(dataset_ref, path=temp_dir, unzip=True)
        zip_path = os.path.join(temp_dir, f"{title}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=file)
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
    return {"data": zip_data, "file_name": f"{title}.zip"}

dataset_search_page()
