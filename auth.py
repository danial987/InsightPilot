import streamlit as st
import re
import hashlib
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Boolean
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2 import errors

# Fetch database configuration from Streamlit secrets
db_config = st.secrets["connections"]["postgresql"]

# Update the database connection URL to disable SSL
DATABASE_URL = f"postgresql+psycopg2://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?sslmode=disable"

# Set up the database connection
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the users table
users = Table(
    'users', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('username', String, unique=True, nullable=False),
    Column('email', String, unique=True, nullable=False),
    Column('password', String, nullable=False),
    Column('is_verified', Boolean, default=False)
)
metadata.create_all(engine)

class Auth:
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
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    hashed_password = self.hash_password(password)
                    cur.execute(
                        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, hashed_password)
                    )
                    conn.commit()
            return True
        except errors.UniqueViolation:
            st.error("Username or email already exists, please choose another one.")
            return False
        except Exception as e:
            st.error(f"Error during registration: {e}")
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
            return True  # Default to True to avoid allowing duplicate in case of error

    def check_email_exists(self, email):
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT email FROM users WHERE email = %s", (email,))
                    user = cur.fetchone()
            return user is not None
        except Exception as e:
            st.error(f"Error during email check: {e}")
            return True  # Default to True to avoid allowing duplicate in case of error

# Email validation function
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

# Password validation function
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[a-zA-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[@$!%*?&]", password):
        return False
    return True

def display_auth_page():
    auth = Auth()

    st.header("Welcome to InsightPilot", divider='violet')

    with st.container(border=True):
        register, login = st.tabs(["Register", "Login"])
    
        with register:
            st.header("Register")
    
            # Check for username availability in real-time
            def check_username():
                if auth.check_username_exists(st.session_state.register_username):
                    st.session_state.username_available = False
                else:
                    st.session_state.username_available = True
    
            # Check for email availability in real-time
            def check_email():
                if not is_valid_email(st.session_state.register_email):
                    st.session_state.email_valid = False
                elif auth.check_email_exists(st.session_state.register_email):
                    st.session_state.email_available = False
                else:
                    st.session_state.email_valid = True
                    st.session_state.email_available = True
    
            # Initialize session state for input tracking
            if "password_started" not in st.session_state:
                st.session_state.password_started = False
    
            if "confirm_password_started" not in st.session_state:
                st.session_state.confirm_password_started = False
    
            # Username input and real-time check
            username = st.text_input("New Username *", key="register_username", on_change=check_username)
            
            # Email input and real-time check
            email = st.text_input("Email *", key="register_email", on_change=check_email)
            
            # Track password interaction and validate password
            def on_password_change():
                st.session_state.password_started = True
    
            password = st.text_input(
                "Password *", 
                type="password", 
                key="register_password", 
                on_change=on_password_change,
                help="Min 8 characters, include letters, numbers, special characters"
            )
    
            # Track confirm password interaction
            def on_confirm_password_change():
                st.session_state.confirm_password_started = True
    
            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                key="confirm_password_unique",  # Unique key
                on_change=on_confirm_password_change
            )
    
            # Validation flags
            username_valid = st.session_state.get("username_available", True)
            email_valid = st.session_state.get("email_valid", True) and st.session_state.get("email_available", True)
            password_valid = is_valid_password(password)
            passwords_match = password == confirm_password and password != ""
    
            # Real-time validation messages
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
    
            # Enable the register button only if all validations pass
            register_disabled = not (username_valid and email_valid and password_valid and passwords_match)
    
            # Only allow registration if username and email are available and passwords match
            if st.button("Register", key="register_button", disabled=register_disabled):
                if auth.register_user(username, email, password):
                    st.success("Registration successful. You can now login.")
                else:
                    st.error("Registration failed. Please try again.")
    
        with login:
            st.header("Login")
            user_identifier = st.text_input("Username or Email", key="login_user_identifier")
            password = st.text_input("Password", type="password", key="login_password")
    
            if st.button("Login", key="login_button"):
                user = auth.authenticate_user(user_identifier, password)
                if user:
                    st.session_state.user_id = user[0]
                    st.session_state.authenticated = True
                    # Use query params to reload the page
                    st.query_params.from_dict({"reload": "true"})
                else:
                    st.error("Invalid credentials or user does not exist")

def logout_user():
    """Handles user logout by resetting session state"""
    st.session_state.user_id = None
    st.session_state.authenticated = False
    # Reload the page using query params
    st.query_params.from_dict({"reload": "true"})
