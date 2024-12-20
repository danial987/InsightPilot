import streamlit as st
import pandas as pd
import io
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler, LabelEncoder
from sklearn.impute import SimpleImputer  
from sklearn.ensemble import IsolationForest  
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTEENN
from dataset import Dataset
import json
from abc import ABC, abstractmethod
import os


class IPreprocessingStrategy(ABC):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("Preprocessing strategies must implement the apply method.")


class PreprocessDataset:
    def __init__(self, strategy: IPreprocessingStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: IPreprocessingStrategy):
        self._strategy = strategy

    def apply_preprocessing(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._strategy.apply(df)


def load_data_with_logging(data, file_format: str):
    """
    Handles reading different file formats (CSV, XLSX) with proper error handling.
    """
    df = pd.DataFrame()  

    try:
        if file_format == 'csv':
            df = Dataset.try_parsing_csv(io.BytesIO(data))  
            if df is None:
                st.error("Failed to parse the CSV file. Please check the file format.")
                return None
        elif file_format == 'xlsx':  
            df = pd.read_excel(io.BytesIO(data), engine='openpyxl') 
            if df is None:
                st.error("Failed to parse the Excel file. Please check the file format.")
                return None
        else:
            st.error("Unsupported file type")
            return pd.DataFrame()
    
    except Exception as e:
        st.error(f"Error parsing the file: {e}")
        return pd.DataFrame()
    
    return df


class RemoveDuplicates(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if not df.duplicated().any():
            st.warning("This dataset has no duplicates.")
            return df

        @st.dialog("Handle Duplicates")
        def show_duplicate_dialog():
            duplicate_rows = df[df.duplicated()]
            st.write("### Duplicates Found :")
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


class EncodeData(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

        if not categorical_columns:
            st.warning("This dataset has no categorical columns to encode.")
            return df

        @st.dialog("Encode Data")
        def show_encode_dialog():
            st.write("### Categorical Columns for Encoding:")
            st.write(categorical_columns)

            encoding_method = st.selectbox("Select encoding method", ["One-Hot Encoding", "Label Encoding", "Binary Encoding", "Frequency Encoding"],
                                           help="Choose how to encode categorical data.")

            encoded_df = df.copy()

            if encoding_method == "One-Hot Encoding":
                encoded_df = pd.get_dummies(df, columns=categorical_columns)
            elif encoding_method == "Label Encoding":
                label_encoders = {}
                for col in categorical_columns:
                    label_encoders[col] = LabelEncoder()
                    encoded_df[col] = label_encoders[col].fit_transform(df[col])

            elif encoding_method == "Binary Encoding":
                binary_encoder = BinaryEncoder(cols=categorical_columns)
                encoded_df = binary_encoder.fit_transform(df)

            elif encoding_method == "Frequency Encoding":
                for col in categorical_columns:
                    freq_encoding = df[col].value_counts(normalize=True)
                    encoded_df[col] = df[col].map(freq_encoding)

            if st.button("Apply Encoding"):
                st.success(f"{encoding_method} has been applied.")
                st.session_state['df_preprocessed'] = encoded_df
                st.session_state['encoding_applied'] = True
                st.session_state['show_before_after_button'] = True
                st.session_state['show_save_button'] = True
                st.session_state['show_encode_dialog'] = False

        if 'show_encode_dialog' not in st.session_state:
            st.session_state['show_encode_dialog'] = True

        if st.session_state['show_encode_dialog']:
            show_encode_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']


class HandleImbalancedData(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        @st.dialog("Handle Imbalanced Data")
        def show_handle_imbalanced_dialog():
            st.write("### Imbalanced Data Handling")

            target_column = st.selectbox("Select the target column", df.columns, help="This column will be used as the class label for balancing.")

            if target_column not in df.columns:
                st.error("Please select a valid target column.")
                return df

            X = df.drop(columns=[target_column]) 
            y = df[target_column]

            if pd.isnull(y).any():
                st.warning("The target column contains missing values. They will be replaced with the most frequent class.")
                y.fillna(y.mode()[0], inplace=True) 

            if pd.api.types.is_numeric_dtype(y):
                y = pd.cut(y, bins=2, labels=[0, 1]) 

            if y.nunique() <= 1:
                st.error("The target column must have at least two distinct classes.")
                return df

            imputer_num = SimpleImputer(strategy='median')
            imputer_cat = SimpleImputer(strategy='most_frequent')

            for col in X.columns:
                if X[col].dtype in ['int64', 'float64']:  
                    X[col] = imputer_num.fit_transform(X[[col]])  
                else: 
                    label_enc = LabelEncoder()
                    X[col] = imputer_cat.fit_transform(X[[col]]).ravel() 
                    X[col] = label_enc.fit_transform(X[col]) 

            balancing_method = st.selectbox("Choose balancing method", ["Oversampling (SMOTE)", "Undersampling", "Combination (SMOTE + Undersampling)"],
                                            help="Choose how to handle imbalanced data.")

            minority_class_size = y.value_counts().min()

            k_neighbors = max(min(minority_class_size - 1, 1), 1)

            balanced_X, balanced_y = X, y

            if balancing_method == "Oversampling (SMOTE)":
                if minority_class_size <= 1:
                    st.warning("SMOTE requires at least 2 samples in the minority class. Consider another method.")
                else:
                    smote = SMOTE(k_neighbors=min(k_neighbors, minority_class_size - 1)) 
                    balanced_X, balanced_y = smote.fit_resample(X, y)
            elif balancing_method == "Undersampling":
                undersample = RandomUnderSampler()
                balanced_X, balanced_y = undersample.fit_resample(X, y.astype(str)) 
            elif balancing_method == "Combination (SMOTE + Undersampling)":
                if minority_class_size <= 1:
                    st.warning("SMOTE requires at least 2 samples in the minority class. Consider another method.")
                else:
                    smote_enn = SMOTEENN(smote=SMOTE(k_neighbors=min(k_neighbors, minority_class_size - 1)))
                    balanced_X, balanced_y = smote_enn.fit_resample(X, y)

            balanced_df = pd.concat([pd.DataFrame(balanced_X, columns=X.columns), pd.DataFrame(balanced_y, columns=[target_column])], axis=1)

            if st.button("Apply Balancing"):
                st.success(f"{balancing_method} has been applied.")
                st.session_state['df_preprocessed'] = balanced_df
                st.session_state['imbalanced_data_handled'] = True
                st.session_state['show_before_after_button'] = True
                st.session_state['show_save_button'] = True
                st.session_state['show_handle_imbalanced_dialog'] = False

        if 'show_handle_imbalanced_dialog' not in st.session_state:
            st.session_state['show_handle_imbalanced_dialog'] = True

        if st.session_state['show_handle_imbalanced_dialog']:
            show_handle_imbalanced_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']
   

class OutlierHandling(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        if not numerical_columns:
            st.warning("This dataset has no numerical columns to check for outliers.")
            return df

        if df[numerical_columns].isnull().values.any():
            st.error("The dataset contains missing values. Please handle missing values before performing outlier detection.")
            return df

        @st.dialog("Handle Outliers")
        def show_outlier_handling_dialog():
            st.write("### Outlier Handling")
            st.write("Numerical columns being analyzed for outliers:")
            st.write(numerical_columns)

            method = st.selectbox("Select outlier detection method", ["Isolation Forest", "Z-Score"],
                                  help="Choose the method for detecting outliers.")
            outlier_df = df.copy()

            if method == "Isolation Forest":
                contamination = st.slider("Contamination (percentage of data expected to be outliers)", 0.01, 0.5, 0.2)
                isolation_forest = IsolationForest(contamination=contamination, random_state=42)

                outliers = isolation_forest.fit_predict(outlier_df[numerical_columns])
                st.write(f"Outliers detected: {sum(outliers == -1)} rows")
                outlier_df = outlier_df[outliers == 1]  

            elif method == "Z-Score":
                threshold = st.slider("Z-Score Threshold", 1.0, 5.0, 2.0)
                z_scores = (outlier_df[numerical_columns] - outlier_df[numerical_columns].mean()) / outlier_df[numerical_columns].std()
                st.write(f"Z-Scores:\n{z_scores}")
                outlier_df = outlier_df[(z_scores.abs() < threshold).all(axis=1)]

            if st.button("Apply Outlier Handling"):
                st.success(f"Outlier handling using {method} has been applied.")
                st.session_state['df_preprocessed'] = outlier_df
                st.session_state['outliers_handled'] = True
                st.session_state['show_before_after_button'] = True
                st.session_state['show_save_button'] = True
                st.session_state['show_outlier_handling_dialog'] = False

        if 'show_outlier_handling_dialog' not in st.session_state:
            st.session_state['show_outlier_handling_dialog'] = True

        if st.session_state['show_outlier_handling_dialog']:
            show_outlier_handling_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']


class DeleteFeatures(IPreprocessingStrategy):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        all_columns = df.columns.tolist()

        if not all_columns:
            st.warning("This dataset has no columns to delete.")
            return df

        @st.dialog("Delete Features")
        def show_delete_features_dialog():
            st.write("### Available Columns:")
            st.write(all_columns)

            columns_to_delete = st.multiselect(
                "Select features (columns) to delete from the dataset:",
                options=all_columns,
                help="Hold Ctrl or Cmd to select multiple columns."
            )

            if columns_to_delete:
                if st.button("Delete Selected Features"):
                    df_cleaned = df.copy()
                    df_cleaned.drop(columns=columns_to_delete, inplace=True)
                    st.success(f"Features {columns_to_delete} have been deleted.")
 
                    st.session_state['df_preprocessed'] = df_cleaned
                    st.session_state['features_deleted'] = True
                    st.session_state['show_before_after_button'] = True
                    st.session_state['show_save_button'] = True
                    st.session_state['show_delete_features_dialog'] = False
            else:
                st.warning("No columns selected for deletion.")

        if 'show_delete_features_dialog' not in st.session_state:
            st.session_state['show_delete_features_dialog'] = True

        if st.session_state['show_delete_features_dialog']:
            show_delete_features_dialog()

        return df if 'df_preprocessed' not in st.session_state else st.session_state['df_preprocessed']


@staticmethod
def calculate_memory_usage(df):
    """Calculates the memory usage of the DataFrame."""
    return df.memory_usage(deep=True).sum()


@staticmethod
def is_hashable(val):
    """Checks if a value is hashable."""
    try:
        hash(val)
    except TypeError:
        return False
    return True


@staticmethod
def make_hashable(df):
    """Converts lists in DataFrame cells to tuples so they are hashable."""
    return df.applymap(lambda x: tuple(x) if isinstance(x, list) else x)


def load_css():
    """Load custom CSS to style the interface."""
    try:
        css_path = os.path.join(os.path.dirname(__file__), "../static/style.css")
        with open(css_path) as f:
            css_code = f.read()
        st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS file not found. Using default styles.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")



def reset_preprocessing_state():
    session_keys_to_reset = ['df_preprocessed', 'duplicates_removed', 'missing_values_filled',
                             'scaling_applied', 'encoding_applied', 'imbalanced_data_handled', 
                             'outliers_handled', 'show_before_after_button', 'show_save_button',
                             'show_duplicates_dialog', 'show_fill_missing_dialog', 
                             'show_scale_features_dialog', 'show_encode_dialog', 'show_handle_imbalanced_dialog',
                             'show_outlier_handling_dialog']
    
    for key in session_keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]


def data_preprocessing_page():
    load_css()
    
    st.header('Data Preprocessing', divider='violet')
    with st.spinner("Loading Please Wait ..."):

        if 'dataset_name_to_preprocess' in st.session_state:
            if 'previous_dataset' not in st.session_state or st.session_state['previous_dataset'] != st.session_state['dataset_name_to_preprocess']:
                reset_preprocessing_state()
                st.session_state['previous_dataset'] = st.session_state['dataset_name_to_preprocess']
    
        if 'df_to_preprocess' in st.session_state and 'dataset_name_to_preprocess' in st.session_state:
            data = st.session_state.df_to_preprocess
    
            if isinstance(data, bytes):
                df = load_data_with_logging(data, file_format=st.session_state.dataset_name_to_preprocess.split('.')[-1])
            else:
                df = data
    
            if df.empty:
                st.error("Unable to load the dataset. Please check for formatting issues.")
                return
    
            df = make_hashable(df)
    
            if 'df_preprocessed' not in st.session_state:
                st.session_state['df_preprocessed'] = df.copy()
    
            dataset_name = st.session_state.dataset_name_to_preprocess
    
            # with st.container(border=True):
            with st.expander(f"Dataset: {dataset_name}"):
                st.dataframe(df)
    
            with st.container(border=True):
                preprocess_options = [
                    "Remove Duplicates", 
                    "Fill Missing Values", 
                    "Scale Features", 
                    "Encode Data", 
                    "Handle Imbalanced Data", 
                    "Handle Outliers", 
                    "Delete Features"
                ]
                selected_preprocess = st.selectbox(
                    "Choose a preprocessing step", 
                    preprocess_options,
                    help="Select a preprocessing technique to apply to the dataset."
                )
                st.session_state['selected_preprocess'] = selected_preprocess
    
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
    
            elif selected_preprocess == "Encode Data":
                if st.session_state.get('encoding_applied', False):
                    st.warning("You've already applied encoding.")
                else:
                    preprocessing_context = PreprocessDataset(EncodeData())
                    if st.button("Apply"):
                        df_preprocessed = preprocessing_context.apply_preprocessing(st.session_state.df_preprocessed)
                        st.session_state.df_preprocessed = df_preprocessed
                        st.session_state['show_before_after_button'] = True
                        st.session_state['show_save_button'] = True
    
            elif selected_preprocess == "Handle Imbalanced Data":
                if st.session_state.get('imbalanced_data_handled', False):
                    st.warning("You've already handled the imbalanced data.")
                else:
                    preprocessing_context = PreprocessDataset(HandleImbalancedData())
                    if st.button("Apply"):
                        df_preprocessed = preprocessing_context.apply_preprocessing(st.session_state.df_preprocessed)
                        st.session_state.df_preprocessed = df_preprocessed
                        st.session_state['show_before_after_button'] = True
                        st.session_state['show_save_button'] = True
    
            elif selected_preprocess == "Handle Outliers":
                if st.session_state.get('outliers_handled', False):
                    st.warning("You've already handled outliers.")
                else:
                    preprocessing_context = PreprocessDataset(OutlierHandling())
                    if st.button("Apply"):
                        df_preprocessed = preprocessing_context.apply_preprocessing(st.session_state.df_preprocessed)
                        st.session_state.df_preprocessed = df_preprocessed
                        st.session_state['show_before_after_button'] = True
                        st.session_state['show_save_button'] = True
    
            elif selected_preprocess == "Delete Features":
                if st.session_state.get('features_deleted', False):
                    st.warning("You've already deleted features.")
                else:
                    preprocessing_context = PreprocessDataset(DeleteFeatures())
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
                col1, col2 = st.columns([6, 1])
            
                with col1:
                    if st.button("Save to Database"):
                        dataset_db = Dataset()
            
                        if 'user_id' not in st.session_state:
                            st.error("User not logged in. Please log in to save datasets.")
                        else:
                            user_id = st.session_state['user_id']  
            
                            if dataset_name:
                                if '.' in dataset_name:
                                    base_name, extension = dataset_name.rsplit('.', 1)
                                else:
                                    base_name, extension = dataset_name, 'csv'
            
                                new_dataset_name = f"{base_name}_preprocessed.{extension}"
            
                                dataset_db.save_to_database(
                                    new_dataset_name,
                                    'csv',
                                    len(st.session_state.df_preprocessed),
                                    st.session_state.df_preprocessed.to_csv(index=False).encode(),
                                    user_id=user_id  
                                )
            
                                st.success(f"Preprocessed dataset saved as '{new_dataset_name}' in the database.")
                            else:
                                st.error("Dataset name is missing. Cannot save.")
    
                with col2:
                    if st.button("Go to Visualization"):
                        st.session_state.df_to_visualize = st.session_state.df_preprocessed
                        st.session_state.dataset_name_to_visualize = st.session_state.dataset_name_to_preprocess
                        st.switch_page("pages/data_visualization.py")

        else:
            st.warning("No dataset selected for preprocessing. Please ensure you're navigating from the appropriate page where the dataset is uploaded or summarized.")

data_preprocessing_page()