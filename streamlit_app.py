import streamlit as st
from st_pages import Page
import auth

# Set page configuration as the first command
st.set_page_config(page_title="InsightPilot", page_icon="🧠")

# Session state for user authentication
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Display logo
st.sidebar.image("static/logo.png", width=180)

# Display logout button if user is authenticated
if st.session_state.authenticated:
    if st.sidebar.button("Logout"):
        auth.logout_user()

# Define the pages for the app
pages = [
    st.Page("pages/dataset_upload.py", title="Dataset Upload", icon="⬆️"),
    st.Page("pages/search_dataset.py", title="Search Dataset", icon="🔍"),
    st.Page("pages/dataset_summary.py", title="Dataset Summary", icon="📊"),
    st.Page("pages/data_preprocessing.py", title="Data Preprocessing", icon="🔧"),
    st.Page("pages/data_visualization.py", title="Data Visualization", icon="📈"),
    st.Page("pages/chatbot.py", title="Chatbot", icon="🤖")
]

# If user is not authenticated, display the authentication page
if not st.session_state.authenticated:
    auth.display_auth_page()
else:
    # If user is authenticated, load the pages
    pg = st.navigation(pages)
    pg.run()
