import streamlit as st
from st_pages import Page
import auth

def load_css():
    """Load custom CSS to style the chatbot interface."""
    try:
        import os
        css_path = os.path.join(os.path.dirname(__file__), 'static/stylebot.css')
        with open(css_path) as f:
            css_code = f.read()
        # with open('static/stylebot.css') as f:
        #     css_code = f.read()
        st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS file not found! Make sure 'static/stylebot.css' exists.")

st.set_page_config(
    layout="wide",  
)
# Inject CSS for primaryColor


if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none;}
            .st-emotion-cache-19ee8pt{
            display:none;}
            .st-emotion-cache-12fmjuu{
            display:none;}
            .st-emotion-cache-hzo1qh{
            display:none;}
            .st-emotion-cache-13ln4jf{
            margin-top: -80px;}
            .st-emotion-cache-13ln4jf {
                width: 100%;
                padding: 6rem 1rem 1rem;
                max-width: 46rem;
            }

            ._link_gzau3_10 {
              visibility: hidden;
            }
            
            ._profileContainer_gzau3_53 {
              visibility: hidden;
            }
            
        </style>
        """,
        unsafe_allow_html=True
    )
    auth.display_auth_page()
    
else:
    
    import os
    logo_path = os.path.join(os.path.dirname(__file__), "static/logo.png")
    st.sidebar.image(logo_path, width=180)


    # st.sidebar.image("static/logo.png", width=180)
    if st.sidebar.button("Logout"):
        auth.logout_user()

    pages = [
        st.Page("pages/dataset.py", title="Dataset", icon="🛢️"),
        st.Page("pages/dataset_summary.py", title="Dataset Summary", icon="📑"),
        st.Page("pages/data_preprocessing.py", title="Data Preprocessing", icon="🛠️"),
        st.Page("pages/data_visualization.py", title="Data Visualization", icon="📶"),
        st.Page("pages/models.py", title="Models", icon="🎲"),
        st.Page("pages/chatbot.py", title="Chatbot", icon="🤖")
    ]

    pg = st.navigation(pages)
    load_css()
    pg.run()