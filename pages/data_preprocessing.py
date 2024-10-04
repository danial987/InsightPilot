import streamlit as st
import pandas as pd
import io  # For StringIO
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler
from database import Dataset

# Interface for preprocessing strategy
class IPreprocessingStrategy:
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("Preprocessing strategies must implement the apply method.")

# Context class for dataset preprocessing
class PreprocessDataset:
    def __init__(self, strategy: IPreprocessingStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: IPreprocessingStrategy):
        self._strategy = strategy

    def apply_preprocessing(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._strategy.apply(df)

# Concrete strategy: Remove Duplicates
class RemoveDuplicates(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if not df.duplicated().any():
            st.warning("This dataset has no duplicates.")
            return df

        @st.dialog("Handle Duplicates")
        def show_duplicate_dialog():
            duplicate_rows = df[df.duplicated()]
            st.write("### Duplicates Found (Highlighted in Green):")
            styled_duplicates = duplicate_rows.style.apply(lambda x: ['background-color: lightgreen' for _ in x], axis=1)
            st.dataframe(styled_duplicates)

            if st.button("Remove Duplicates"):
                df_cleaned = df.drop_duplicates().copy()
                st.success("All the duplicates are removed successfully.")
                st.session_state['df_preprocessed'] = df_cleaned
                st.session_state['duplicates_removed'] = True
                st.session_state['show_before_after_button'] = True
                st.session_state['show_save_button'] = True
                st.session_state['show_duplicates_dialog'] = False

        if 'show_duplicates_dialog' not in st.session_state:
            st.session_state['show_duplicates_dialog'] = True

        if st.session_state['show_duplicates_dialog']:
            show_duplicate_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']

# Concrete strategy: Fill Missing Values
class FillMissingValues(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if not df.isnull().values.any():
            st.warning("This dataset has no missing values.")
            return df

        missing_columns = df.columns[df.isnull().any()].tolist()
        missing_summary = df.isnull().sum()

        @st.dialog("Handle Missing Values")
        def show_fill_missing_dialog():
            st.write("### Columns with Missing Values:")
            st.dataframe(missing_summary[missing_summary > 0])

            filled_df = df.copy()
            for col in missing_columns:
                col_type = df[col].dtype

                st.write(f"#### How would you like to fill missing values in `{col}`?")

                if col_type in ['int64', 'float64']:
                    fill_option = st.selectbox(f"Fill method for `{col}` (Numerical)", ["Mean", "Median", "Mode", "Constant"],
                                               help="Select how to fill missing numerical values.")
                    if fill_option == "Mean":
                        filled_df[col] = df[col].fillna(df[col].mean())
                    elif fill_option == "Median":
                        filled_df[col] = df[col].fillna(df[col].median())
                    elif fill_option == "Mode":
                        filled_df[col] = df[col].fillna(df[col].mode()[0])
                    elif fill_option == "Constant":
                        constant_value = st.number_input(f"Enter a constant value for `{col}`")
                        filled_df[col] = df[col].fillna(constant_value)

                else:
                    fill_option = st.selectbox(f"Fill method for `{col}` (Categorical)", ["Mode", "Constant"],
                                               help="Select how to fill missing categorical values.")
                    if fill_option == "Mode":
                        filled_df[col] = df[col].fillna(df[col].mode()[0])
                    elif fill_option == "Constant":
                        constant_value = st.text_input(f"Enter a constant value for `{col}`")
                        filled_df[col] = df[col].fillna(constant_value)

            if st.button("Apply Filling"):
                st.success("Missing values have been filled.")
                st.session_state['df_preprocessed'] = filled_df
                st.session_state['missing_values_filled'] = True
                st.session_state['show_before_after_button'] = True
                st.session_state['show_save_button'] = True
                st.session_state['show_fill_missing_dialog'] = False

        if 'show_fill_missing_dialog' not in st.session_state:
            st.session_state['show_fill_missing_dialog'] = True

        if st.session_state['show_fill_missing_dialog']:
            show_fill_missing_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']

# Concrete strategy: Scale Features
class ScaleFeatures(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        if not numerical_columns:
            st.warning("This dataset has no numerical columns to scale.")
            return df

        @st.dialog("Scale Features")
        def show_scale_features_dialog():
            st.write("### Numerical Columns for Scaling:")
            st.write(numerical_columns)

            scale_method = st.selectbox("Select scaling method", ["Standardization (Mean=0, Std=1)",
                                                                  "Normalization (0-1 range)",
                                                                  "Robust Scaling",
                                                                  "MaxAbs Scaling"],
                                        help="Choose the scaling method to apply to the dataset.")

            scaled_df = df.copy()

            if scale_method == "Standardization (Mean=0, Std=1)":
                scaler = StandardScaler()
            elif scale_method == "Normalization (0-1 range)":
                scaler = MinMaxScaler()
            elif scale_method == "Robust Scaling":
                scaler = RobustScaler()
            elif scale_method == "MaxAbs Scaling":
                scaler = MaxAbsScaler()

            scaled_df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

            if st.button("Apply Scaling"):
                st.success("Scaling has been applied.")
                st.session_state['df_preprocessed'] = scaled_df
                st.session_state['scaling_applied'] = True
                st.session_state['show_before_after_button'] = True
                st.session_state['show_save_button'] = True
                st.session_state['show_scale_features_dialog'] = False

        if 'show_scale_features_dialog' not in st.session_state:
            st.session_state['show_scale_features_dialog'] = True

        if st.session_state['show_scale_features_dialog']:
            show_scale_features_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']


# Main page for preprocessing
def load_css():
    with open('static/style.css') as f:
        css_code = f.read()
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

def reset_preprocessing_state():
    session_keys_to_reset = ['df_preprocessed', 'duplicates_removed', 'missing_values_filled',
                             'scaling_applied', 'show_before_after_button', 'show_save_button',
                             'show_duplicates_dialog', 'show_fill_missing_dialog', 'show_scale_features_dialog']
    
    for key in session_keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

def data_preprocessing_page():
    load_css()
    
    st.header('Data Preprocessing', divider='violet')

    if 'dataset_name_to_preprocess' in st.session_state:
        if 'previous_dataset' not in st.session_state or st.session_state['previous_dataset'] != st.session_state['dataset_name_to_preprocess']:
            reset_preprocessing_state()
            st.session_state['previous_dataset'] = st.session_state['dataset_name_to_preprocess']

    if 'df_to_preprocess' in st.session_state and 'dataset_name_to_preprocess' in st.session_state:
        data = st.session_state.df_to_preprocess
        
        if isinstance(data, bytes):
            df = pd.read_csv(io.StringIO(data.decode('utf-8')))
        else:
            df = data

        if 'df_preprocessed' not in st.session_state:
            st.session_state['df_preprocessed'] = df.copy()

        dataset_name = st.session_state.dataset_name_to_preprocess
        with st.container(border=True):
            st.write(f"Dataset: {dataset_name}")

        with st.container(border=True):
            preprocess_options = ["Remove Duplicates", "Fill Missing Values", "Scale Features"]
            selected_preprocess = st.selectbox("Choose a preprocessing step", preprocess_options,
                                               help="Choose a preprocessing technique: 'Remove Duplicates', 'Fill Missing Values', or 'Scale Features'.")

        if selected_preprocess == "Remove Duplicates":
            if st.session_state.get('duplicates_removed', False):
                st.warning("No duplicates found. You've already removed duplicates.")
            else:
                preprocessing_context = PreprocessDataset(RemoveDuplicates())
                if st.button("Apply"):
                    df_preprocessed = preprocessing_context.apply_preprocessing(st.session_state.df_preprocessed)
                    st.session_state.df_preprocessed = df_preprocessed
                    st.session_state['show_before_after_button'] = True
                    st.session_state['show_save_button'] = True

        elif selected_preprocess == "Fill Missing Values":
            if st.session_state.get('missing_values_filled', False):
                st.warning("No missing values found. You've already filled missing values.")
            else:
                preprocessing_context = PreprocessDataset(FillMissingValues())
                if st.button("Apply"):
                    df_preprocessed = preprocessing_context.apply_preprocessing(st.session_state.df_preprocessed)
                    st.session_state.df_preprocessed = df_preprocessed
                    st.session_state['show_before_after_button'] = True
                    st.session_state['show_save_button'] = True

        elif selected_preprocess == "Scale Features":
            if st.session_state.get('scaling_applied', False):
                st.warning("You've already applied scaling.")
            else:
                preprocessing_context = PreprocessDataset(ScaleFeatures())
                if st.button("Apply"):
                    df_preprocessed = preprocessing_context.apply_preprocessing(st.session_state.df_preprocessed)
                    st.session_state.df_preprocessed = df_preprocessed
                    st.session_state['show_before_after_button'] = True
                    st.session_state['show_save_button'] = True

        if st.session_state.get('show_before_after_button', False):
            with st.container(border=True):
                if st.button("Show Before and After"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("### Before Preprocessing")
                        st.dataframe(df)
                    with col2:
                        st.write("### After Preprocessing")
                        st.dataframe(st.session_state.df_preprocessed)

        if st.session_state.get('show_save_button', False):
            with st.container(border=True):
                if st.button("Save to Database"):
                    dataset_db = Dataset()

                    base_name, extension = dataset_name.rsplit('.', 1)
                    new_dataset_name = f"{base_name}_preprocessed.{extension}"

                    dataset_db.save_to_database(
                        new_dataset_name,
                        'csv',
                        len(st.session_state.df_preprocessed),
                        st.session_state.df_preprocessed.to_csv(index=False).encode()
                    )
                    st.success(f"Preprocessed dataset saved as '{new_dataset_name}' in the database.")

    else:
        st.warning("No dataset selected for preprocessing. Please ensure you're navigating from the appropriate page where dataset is uploaded or summarized.")

data_preprocessing_page()
