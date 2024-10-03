import streamlit as st


def load_css():
    with open('static/style.css') as f:
        css_code = f.read()
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

def dataset_search_page():
    load_css()
    st.header('Search Kaggle Datasets', divider='violet')
    st.write('Search for datasets on Kaggle and download them to your local machine.')
    st.write('This feature is comming soon!')



dataset_search_page()
