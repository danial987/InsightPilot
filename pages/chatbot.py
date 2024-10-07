import streamlit as st
import pandas as pd
from transformers import pipeline
import uuid
import io

from pages.dataset_summary import DatasetSummary

def load_custom_css():
    custom_css = """
    <style>
    .st-emotion-cache-1eo1tir {
        width: 100%;
        padding: 6rem 1rem 1rem;
        max-width: 60rem;
    }

    #MainMenu,
    header {
      visibility: hidden;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

class Chatbot:
    def __init__(self):
        self.nlp = pipeline('text-generation', model='gpt2')
        self.qa_model = pipeline('question-answering')

        if 'session_id' not in st.session_state:
            st.session_state['session_id'] = str(uuid.uuid4()) 

        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []

    def handle_specific_questions(self, df, question):
        question_lower = question.lower()

        if 'how many rows' in question_lower:
            st.write(f"The dataset has {len(df)} rows.")
            return None  
    
        if 'how many columns' in question_lower or 'number of features' in question_lower or 'number of columns' in question_lower:
            st.write(f"The dataset has {len(df.columns)} columns.")
            return None

        if 'summary' in question_lower or 'describe' in question_lower:
            st.write(self.generate_dataset_summary(df))
            return None

        if 'missing values' in question_lower:
            missing_cells = df.isnull().sum().sum()
            st.write(f"The dataset has {missing_cells} missing values.") if missing_cells else st.write("The dataset has no missing values.")
            return None

        if 'duplicate rows' in question_lower:
            duplicate_rows = df.duplicated().sum()
            st.write(f"The dataset has {duplicate_rows} duplicate rows.") if duplicate_rows else st.write("The dataset has no duplicate rows.")
            return None

        if 'numerical features' in question_lower or 'numerical analysis' in question_lower:
            numerical_features = df.select_dtypes(include=[float, int]).columns.tolist()
            if numerical_features:
                st.write("Numerical Features:")
                st.dataframe(df[numerical_features].describe())
            else:
                st.write("No numerical features available in the dataset.")
            return None

        if 'categorical features' in question_lower or 'categorical analysis' in question_lower:
            categorical_features = df.select_dtypes(include=['object']).columns.tolist()
            if categorical_features:
                st.write("Categorical Features:")
                st.dataframe(df[categorical_features].describe(include='all'))
            else:
                st.write("No categorical features available in the dataset.")
            return None

        if 'correlation matrix' in question_lower:
            numerical_features = df.select_dtypes(include=[float, int])
            if numerical_features.shape[1] > 1:
                st.write("Correlation Matrix:")
                st.dataframe(numerical_features.corr())
            else:
                st.write("Not enough numerical columns for a correlation matrix.")
            return None

        if 'distribution' in question_lower:
            numerical_features = df.select_dtypes(include=[float, int])
            if not numerical_features.empty:
                st.write("Skewness:")
                st.dataframe(numerical_features.apply(lambda x: x.skew()).to_frame('Skewness'))
    
                st.write("Kurtosis:")
                st.dataframe(numerical_features.apply(lambda x: x.kurtosis()).to_frame('Kurtosis'))
            else:
                st.write("No numerical features available for distribution analysis.")
            return None

        if 'first rows' in question_lower or 'show first' in question_lower:
            st.write("First rows of data:")
            st.dataframe(df.head())
            return None

        if 'middle rows' in question_lower:
            middle_idx = len(df) // 2
            st.write("Middle rows of data:")
            st.dataframe(df.iloc[middle_idx - 2:middle_idx + 3])
            return None

        if 'last rows' in question_lower or 'show last' in question_lower:
            st.write("Last rows of data:")
            st.dataframe(df.tail())
            return None

        if 'top' in question_lower and 'categories' in question_lower:
            column_name = question_lower.split("in")[-1].strip().replace("[column_name]", "").strip()
            if column_name in df.columns:
                if pd.api.types.is_categorical_dtype(df[column_name]) or df[column_name].dtype == object:
                    top_n = 5 
                    top_categories = df[column_name].value_counts().head(top_n)
                    st.write(f"Top {top_n} categories in '{column_name}':")
                    st.table(top_categories)
                    return None
                else:
                    st.write(f"'{column_name}' is not a categorical column.")
                    return None
            else:
                st.write(f"Column '{column_name}' not found in the dataset.")
                return None
    
        return None 

    def generate_dataset_summary(self, df):
        description = DatasetSummary.display_summary(df, st.session_state.get('dataset_name', 'Dataset'))
        return description

    def generate_numerical_features_analysis(self, df):
        numerical_features = df.select_dtypes(include=[float, int]).columns.tolist()
        if not numerical_features:
            return "No numerical features available in the dataset."
        
        basic_stats = df[numerical_features].describe().to_string()
        return f"Numerical Features Analysis:\n{basic_stats}"

    def generate_categorical_features_analysis(self, df):
        categorical_features = df.select_dtypes(include=['object']).columns.tolist()
        if not categorical_features:
            return "No categorical features available in the dataset."
        
        return f"Categorical Features:\n{', '.join(categorical_features)}"

    def generate_correlation_matrix(self, df):
        corr_matrix = df.corr().to_string()
        return f"Correlation Matrix:\n{corr_matrix}"

    def generate_distribution_analysis(self, df):
        numerical_features = df.select_dtypes(include=[float, int]).columns.tolist()
        skewness_info = {}
        kurtosis_info = {}

        for feature in numerical_features:
            skewness_info[feature] = df[feature].skew()
            kurtosis_info[feature] = df[feature].kurtosis()

        skewness_str = "\n".join([f"- {feature}: {skewness:.2f}" for feature, skewness in skewness_info.items()])
        kurtosis_str = "\n".join([f"- {feature}: {kurtosis:.2f}" for feature, kurtosis in kurtosis_info.items()])

        return f"Skewness:\n{skewness_str}\n\nKurtosis:\n{kurtosis_str}"

    def answer_dataset_question(self, df, user_question):
        try:
            specific_answer = self.handle_specific_questions(df, user_question)
            if specific_answer:
                return specific_answer

            context = f"Columns: {', '.join(df.columns)}\nFirst rows:\n{df.head(5).to_string(index=False)}"
            qa_input = {"question": user_question, "context": context}
            result = self.qa_model(qa_input)

            return result['answer']
        except Exception as e:
            return f"Error processing the dataset question: {str(e)}"

    def answer_general_question(self, user_question):
        try:
            response = self.nlp(user_question, max_length=50, num_return_sequences=1)
            return response[0]['generated_text']
        except Exception as e:
            return f"Error processing the general question: {str(e)}"

    def load_dataset(self):
        dataset_data = st.session_state.get('df_to_chat', None)
        if dataset_data:
            if isinstance(dataset_data, bytes):
                try:
                    df = pd.read_csv(io.BytesIO(dataset_data))
                except pd.errors.ParserError:
                    df = pd.read_json(io.BytesIO(dataset_data))
            else:
                df = dataset_data

            return df, st.session_state['dataset_name_to_chat']
        return None, None

    def run(self):
        load_custom_css()

        df, dataset_name = self.load_dataset()

        if df is not None and dataset_name is not None:
            st.title(f"Chat with your Dataset: {dataset_name} 🧠")

            for chat in st.session_state['chat_history']:
                st.chat_message(chat['role']).write(chat['message'])
   
            prompt = st.chat_input(f"Ask a question about {dataset_name}!")
            if prompt:
                st.session_state['chat_history'].append({'role': 'user', 'message': prompt})
                st.chat_message('user').write(prompt)

                response = self.answer_dataset_question(df, prompt)

                st.session_state['chat_history'].append({'role': 'assistant', 'message': response})
                st.chat_message('assistant').write(response)

        else:
            st.error("No dataset selected. Please go back and select a dataset.")

chatbot = Chatbot()
chatbot.run()
