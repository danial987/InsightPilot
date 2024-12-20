import streamlit as st
import re
import hashlib
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Boolean
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2 import errors
import time


db_config = st.secrets["connections"]["postgresql"]

DATABASE_URL = f"postgresql+psycopg2://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?sslmode=disable"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

users = Table(
    'users', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('username', String, unique=True, nullable=False),
    Column('email', String, unique=True, nullable=False),
    Column('password', String, nullable=False),
)

class User:
    def __init__(self):
        self.users = users
        self.Session = sessionmaker(bind=engine)

    @staticmethod
    def connect_db():
        return psycopg2.connect(
            database=db_config['database'],
            user=db_config['username'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port'],
            sslmode='disable'
        )

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, email, password):
     try:
         print(f"Connecting to DB...")  
         with self.connect_db() as conn:
             print(f"Connected to DB: {conn}")
             with conn.cursor() as cur:
                 hashed_password = self.hash_password(password)
                 print(f"Attempting to execute query with username: {username}, email: {email}")  
                 cur.execute(
                     "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                     (username, email, hashed_password)
                 )
                 conn.commit()
         return True
     except Exception as e:
         print(f"Error in register_user: {e}") 
         return False

    def authenticate_user(self, user_identifier, password):
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    hashed_password = self.hash_password(password)
                    cur.execute(
                        "SELECT user_id FROM users WHERE (username = %s OR email = %s) AND password = %s",
                        (user_identifier, user_identifier, hashed_password)
                    )
                    user = cur.fetchone()
            return user
        except Exception as e:
            st.error(f"Error during authentication: {e}")
            return None

    def check_username_exists(self, username):
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT username FROM users WHERE username = %s", (username,))
                    user = cur.fetchone()
            return user is not None
        except Exception as e:
            st.error(f"Error during username check: {e}")
            return True 
    def check_email_exists(self, email):
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT email FROM users WHERE email = %s", (email,))
                    user = cur.fetchone()
            return user is not None
        except Exception as e:
            st.error(f"Error during email check: {e}")
            return True 

    def get_username(self, user_id):
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
                    user = cur.fetchone()
            return user[0] if user else "Unknown User"
        except Exception as e:
            st.error(f"Error fetching username: {e}")
            return "Unknown User"

def is_valid_email(email):
    email_regex = (
        r"^(?!\.)"                   
        r"[a-zA-Z0-9_.+-]+"         
        r"(?<!\.)@"                 
        r"[a-zA-Z0-9-]+"           
        r"(\.[a-zA-Z]{2,})+$"        
    )
    return bool(re.match(email_regex, email)) and ".." not in email

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[a-zA-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[@$!%*?&#]", password):
        return False
    return True


def display_auth_page():
    user = User()

    # Custom CSS for the right column background
    st.markdown(
        """
        <style>
        .st-emotion-cache-1jicfl2 {
            padding: 2rem 3rem 3rem 3rem; 
            background-color: #f9f9f9; 
            border-left: 5px solid #9645ff; 
            border-radius: 10px; 
            margin: 5rem 6rem 3rem 6rem; 
            margin-top: 6rem;
            box-shadow: 0px 6px 7px rgba(150, 69, 255, 0.2);
            max-width: 1300px;
        }

        .st-emotion-cache-fia5ja {
            width: 1199px;
            position: relative;
            display: flex;
            flex: 1 1 0%;
            flex-direction: column;
            gap: 0.01rem;
        }

        .st-emotion-cache-6awftf{
            visibility: hidden;
    
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # Define columns: intro_col for logo and description, auth_col for login/register
    intro_col, auth_col = st.columns([0.65, 0.35])

    # Left Column: Introductory Section
    with intro_col:
        st.markdown(
            """

            <h2 style="color: #333; font-family: Arial, sans-serif; text-align: left; margin-bottom: 1rem;">Welcome to InsightPilot 👾</h2>
            <p style="font-size: 16px; color: #555; line-height: 1.6; margin-bottom: 1.5rem;">
                InsightPilot is your AI-powered companion for turning complex data into simple and actionable insights
            </p>


            """,
            unsafe_allow_html=True,
        )

        import os
        authimg_path = os.path.join(os.path.dirname(__file__), "static/auth-vector.png")
        # st.sidebar.image(authimg_path, width=180)
        st.image(authimg_path, caption="Navigate the Data Sikes with Confidence")

    # Right Column: Authentication Section
    with auth_col:
        st.markdown('<div class="auth-col">', unsafe_allow_html=True)

        login, register = st.tabs(["🔐 Login", "👨🏻‍💻 Register"])

        # Registration Tab
        with register:
            st.write("#### Register")

            def check_username():
                if user.check_username_exists(st.session_state.register_username):
                    st.session_state.username_available = False
                else:
                    st.session_state.username_available = True

            def check_email():
                if not is_valid_email(st.session_state.register_email):
                    st.session_state.email_valid = False
                elif user.check_email_exists(st.session_state.register_email):
                    st.session_state.email_available = False
                else:
                    st.session_state.email_valid = True
                    st.session_state.email_available = True

            if "password_started" not in st.session_state:
                st.session_state.password_started = False

            if "confirm_password_started" not in st.session_state:
                st.session_state.confirm_password_started = False

            username = st.text_input("New Username *", key="register_username", on_change=check_username)
            email = st.text_input("Email *", key="register_email", on_change=check_email)

            def on_password_change():
                st.session_state.password_started = True

            password = st.text_input(
                "Password *",
                type="password",
                key="register_password",
                on_change=on_password_change,
                help="Min 8 characters, include letters, numbers, special characters",
            )

            def on_confirm_password_change():
                st.session_state.confirm_password_started = True

            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                key="confirm_password_unique",
                on_change=on_confirm_password_change,
            )

            username_valid = st.session_state.get("username_available", True)
            email_valid = st.session_state.get("email_valid", True) and st.session_state.get("email_available", True)
            password_valid = is_valid_password(password)
            passwords_match = password == confirm_password and password != ""

            if not username_valid:
                st.error("Username is already taken, please choose another.")
            if not email_valid:
                st.error("Invalid or already registered email.")
            if st.session_state.password_started and not password_valid:
                st.error("Password must be at least 8 characters long and include letters, numbers, and special characters.")
            if st.session_state.confirm_password_started:
                if passwords_match:
                    st.success("Passwords match!")
                else:
                    st.error("Passwords do not match!")

            register_disabled = not (username_valid and email_valid and password_valid and passwords_match)

            if st.button("Register", key="register_button", disabled=register_disabled):
                if user.register_user(username, email, password):
                    st.success("Registration successful. You can now login.")
                else:
                    st.error("Registration failed. Please try again.")

        # Login Tab
        with login:
            st.write("#### Login")
            user_identifier = st.text_input("Username or Email", key="login_user_identifier")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", key="login_button"):
                authenticated_user = user.authenticate_user(user_identifier, password)
                if authenticated_user:
                    st.session_state.user_id = authenticated_user[0]
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials or user does not exist.")




def logout_user():
    """Handles user logout by resetting session state"""
    st.session_state.user_id = None
    st.session_state.authenticated = False
    st.rerun()