import streamlit as st

def load_css():
    with open('static/style.css') as f:
        css_code = f.read()
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

def chatbot_page():
    load_css()
    st.title("")
    st.header('Chatbot', divider='violet')

    st.write("This feature is coming soon.")

chatbot_page()
