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

def categorize_by_time(datasets):
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

def dataset_upload_page():
    load_css()
    st.header('Upload your dataset', divider='violet')

    if 'uploaded' not in st.session_state:
        st.session_state.uploaded = False
    if 'show_summary_button' not in st.session_state:
        st.session_state.show_summary_button = False
    if 'rename_action_state' not in st.session_state:
        st.session_state.rename_action_state = {}

    with st.container(border=True):
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "json"])

        if uploaded_file is not None:
            file_name = uploaded_file.name
            file_format = file_name.split('.')[-1]
            file_size = uploaded_file.size
            data = uploaded_file.getvalue()

            if dataset_db.dataset_exists(file_name):
                st.warning("Dataset with this name already exists.")
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
                        st.session_state.show_summary_button = True  # Set flag to show summary button
                        progress_text.text("")  # Clear the progress text
                        progress_bar.empty()  # Clear the progress bar

                except pd.errors.ParserError as e:
                    st.error(f"Error parsing the file: {e}")
                    return
                except json.JSONDecodeError as e:
                    st.error(f"Error decoding JSON: {e}")
                    return
                except Exception as e:
                    st.error(f"Error reading the file: {e}")
                    return

        if st.session_state.show_summary_button:
            if st.button("View Data Summary"):
                st.session_state.show_summary_button = False  # Hide the button after navigating
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
            col1, col2, col3, col4, col5 = st.columns([7, 3, 3, 4, 3])
            with col1:
                st.write("**Name**")
            with col2:
                st.write("**Format**")
            with col3:
                st.write("**Size**")
            with col4:
                st.write("**Last Accessed**")
            with col5:
                st.write("**Action**")
            st.write('</div>', unsafe_allow_html=True)

            if isinstance(filter_date, tuple) and len(filter_date) == 2:
                start_date, end_date = filter_date
            else:
                start_date, end_date = datetime.date(2024, 1, 1), datetime.date.today()

            filtered_datasets = [
                ds for ds in datasets_list 
                if search_query.lower() in ds.name.lower() and 
                (filter_format == "All" or ds.file_format == filter_format) and 
                (ds.file_size <= max_size * 1024 * 1024) and 
                (start_date <= ds.last_accessed.date() <= end_date)
            ]

            filtered_datasets.sort(key=lambda x: x.last_accessed, reverse=True)

            categorized_datasets = categorize_by_time(filtered_datasets)

            for category, datasets in categorized_datasets.items():
                if datasets:
                    st.write(f"##### {category}")
                    for ds in datasets:
                        st.write('<div class="recent-file-item">', unsafe_allow_html=True)
                        col2, col3, col4, col5, col6 = st.columns([6, 3, 3, 4, 3])

                        with col2:
                            dataset_name = ds.name.split('.')[0]
                            st.write(f"{dataset_name}")
                        with col3:
                            st.write(f"{ds.file_format.upper()}")
                        with col4:
                            st.write(f"{round(ds.file_size / (1024 * 1024), 2)} MB")
                        with col5:
                            st.write(f"{ds.last_accessed.strftime('%Y-%m-%d %H:%M:%S')}")
                        with col6:
                            action_key = f"action_{ds.id}"
                            action = st.selectbox("", ["Select", "View Summary", "Preprocessing", "Visualization", "Chat", "Share", "Rename", "Delete"], key=action_key, index=st.session_state.rename_action_state.get(ds.id, 0))
                            if action == "View Summary":
                                view_dataset_summary(ds.id)
                            elif action == "Delete":
                                delete_dataset(ds.id)
                            elif action == "Rename":
                                st.session_state.rename_action_state[ds.id] = 6  # Keep the state at "Rename"
                                st.session_state['show_rename_dialog'] = True
                                st.session_state['current_rename_id'] = ds.id
                                st.session_state['current_rename_name'] = ds.name.split('.')[0]  # Show the name without extension
                            else:
                                st.session_state.rename_action_state[ds.id] = 0  # Reset to "Select" after rename
                        st.write('</div>', unsafe_allow_html=True)
            st.write('</div>', unsafe_allow_html=True)

            if not filtered_datasets:
                st.write(f"You don't have any datasets matching the selected filters.")
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
        dataset_db.update_last_accessed(dataset_id)
        st.switch_page("pages/dataset_summary.py")

def delete_dataset(dataset_id):
    dataset_db.delete_dataset(dataset_id)
    st.experimental_rerun()

@st.experimental_dialog("Rename")
def show_rename_dialog():
    dataset_id = st.session_state['current_rename_id']
    current_name = st.session_state['current_rename_name']
    new_name = st.text_input("Please enter a new name for the item:", value=current_name)
    col1, col2 = st.columns(2)
    if col1.button("Cancel"):
        st.session_state['show_rename_dialog'] = False
        st.session_state.rename_action_state[dataset_id] = 0  # Reset to "Select"
        st.experimental_rerun()
    if col2.button("Rename"):
        if dataset_db.dataset_exists(new_name):
            st.error("Dataset with this name already exists.")
        else:
            dataset_db.rename_dataset(dataset_id, new_name)
            st.session_state['show_rename_dialog'] = False
            st.session_state.rename_action_state[dataset_id] = 0  # Reset to "Select"
            st.experimental_rerun()  # Ensure the recent files list is updated without full page reload

if 'show_rename_dialog' not in st.session_state:
    st.session_state['show_rename_dialog'] = False

if st.session_state['show_rename_dialog']:
    show_rename_dialog()

dataset_upload_page()