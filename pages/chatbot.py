import streamlit as st
import pandas as pd
import openai
import uuid
import io


openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")
if openai_api_key:
    openai.api_key = openai_api_key
else:
    st.warning("Please provide an API key to proceed.")

def load_css():
    """Load custom CSS to style the chatbot interface."""
    try:
        with open('static/stylebot.css') as f:
            css_code = f.read()
        st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS file not found! Make sure 'static/stylebot.css' exists.")


class Chatbot:
    def __init__(self):
        """Initialize the chatbot, setting up session state and chat history."""
        self.initialize_session()

    def initialize_session(self):
        """Initialize session state variables."""
        if 'session_id' not in st.session_state:
            st.session_state['session_id'] = str(uuid.uuid4())

        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []


    def reset_chat_history(self):
        """Clear the chat history when switching datasets."""
        st.session_state['chat_history'] = []


    def load_dataset(self):
        """Load the dataset from session state, return the DataFrame and its name."""
        dataset_data = st.session_state.get('df_to_chat', None)
        dataset_name = st.session_state.get('dataset_name_to_chat', None)

        if dataset_data is None:
            st.error("No dataset found in session state.")
            return None, None

        df = self.convert_dataset_to_dataframe(dataset_data)
        return df, dataset_name


    def convert_dataset_to_dataframe(self, dataset_data):
        """Convert the dataset bytes into a pandas DataFrame."""
        try:
            if isinstance(dataset_data, bytes):
                try:
                    return pd.read_csv(io.BytesIO(dataset_data))
                except pd.errors.ParserError:
                    return pd.read_json(io.BytesIO(dataset_data))
            else:
                return dataset_data
        except Exception as e:
            st.error(f"Failed to load dataset: {str(e)}")
            return None


    def call_openai(self, prompt, df):
        """Generate detailed responses using OpenAI API with dataset context."""
        full_prompt = self.build_openai_prompt(prompt, df)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI that helps answer questions related to datasets, providing detailed, elaborative explanations."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=200,  
                temperature=0.6 
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"


    def build_openai_prompt(self, user_prompt, df):
        """Build the prompt for OpenAI by including detailed context from the dataset."""
        dataset_summary = self.generate_dataset_summary(df)
        full_prompt = f"{user_prompt}\n\nDataset Context:\n{dataset_summary}"
        return full_prompt


    def generate_dataset_summary(self, df):
        """Generate a detailed summary of the dataset, including column details and basic statistics."""
        try:
            column_info = self.get_column_information(df)
            missing_values_info = self.get_missing_values_info(df)
            numeric_summary = self.get_numeric_summary(df)

            dataset_summary = (
                f"Columns in the dataset:\n{column_info}\n\n"
                f"Missing values:\n{missing_values_info}\n\n"
                f"Summary statistics for numeric columns:\n{numeric_summary}\n\n"
                f"First 5 rows of the dataset:\n{df.head(5).to_string(index=False)}"
            )
            return dataset_summary
        except Exception as e:
            return f"Error generating dataset summary: {str(e)}"


    def get_column_information(self, df):
        """Get detailed information about dataset columns, including their types."""
        column_info = []
        for col in df.columns:
            dtype = df[col].dtype
            column_info.append(f"- {col}: {dtype}")
        return "\n".join(column_info)


    def get_missing_values_info(self, df):
        """Check for missing values in the dataset."""
        missing_info = df.isnull().sum()
        if missing_info.sum() == 0:
            return "No missing values in the dataset."
        else:
            missing_report = "\n".join([f"- {col}: {missing_info[col]} missing values" for col in df.columns if missing_info[col] > 0])
            return missing_report


    def get_numeric_summary(self, df):
        """Generate summary statistics for numeric columns in the dataset."""
        numeric_columns = df.select_dtypes(include=['float64', 'int64'])
        if numeric_columns.empty:
            return "No numeric columns found in the dataset."
        else:
            return numeric_columns.describe().to_string()


    def run(self):
        """Run the chatbot, handling user input and generating responses."""
        load_css()
        df, dataset_name = self.load_dataset()

        if df is not None and dataset_name is not None:
            st.header(f"Chat with your Dataset: {dataset_name} 🧠", divider='violet')

            for chat in st.session_state['chat_history']:
                st.chat_message(chat['role']).write(chat['message'])

            user_input = st.chat_input(f"Ask a question about {dataset_name}!")
            if user_input:
                self.append_chat_history('user', user_input)

                response = self.call_openai(user_input, df)

                self.append_chat_history('assistant', response)

            self.export_chat_history()

        else:
            st.error("No dataset selected. Please go back and select a dataset.")


    def append_chat_history(self, role, message):
        """Append the user or assistant message to the chat history."""
        st.session_state['chat_history'].append({'role': role, 'message': message})
        st.chat_message(role).write(message)


    def export_chat_history(self):
        """Allow the user to export the chat history as a text file."""
        if st.session_state.get('chat_history'):
            chat_history_text = self.format_chat_history()

            st.download_button(
                label="Download Chat History",
                data=chat_history_text,
                file_name="chat_history.txt",
                mime="text/plain"
            )


    def format_chat_history(self):
        """Format chat history as a readable text."""
        formatted_history = []
        for chat in st.session_state['chat_history']:
            role = "User" if chat['role'] == 'user' else "Assistant"
            formatted_history.append(f"{role}: {chat['message']}\n")
        return "".join(formatted_history)
        

chatbot = Chatbot()
chatbot.run()
