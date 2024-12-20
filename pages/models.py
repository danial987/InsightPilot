import streamlit as st
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression as SklearnLogisticRegression
from sklearn.metrics import (
    precision_recall_curve,
    roc_curve,
    auc,
    mean_squared_error,
    r2_score,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    log_loss,
    confusion_matrix,
    matthews_corrcoef,
    cohen_kappa_score,
    balanced_accuracy_score,
    roc_auc_score,
)
from scipy.stats import f
from sklearn.linear_model import LinearRegression as SklearnLinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from pandas.api.types import is_numeric_dtype
from sklearn.linear_model import Lasso
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
import io
from dataset import Dataset 
from abc import ABC, abstractmethod

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

class IModelStrategy(ABC):
    def __init__(self):
        self.dataset = Dataset()  

    def load_dataset(self, dataset_id, user_id):
        dataset_record = self.dataset.get_dataset_by_id(dataset_id, user_id)
        if not dataset_record:
            raise ValueError("Dataset not found or not accessible.")
        self.dataset.update_last_accessed(dataset_id, user_id)
        file_data = dataset_record['data']
        file_format = dataset_record['file_format']
        return self._load_data_from_bytes(file_data, file_format)

    def _load_data_from_bytes(self, data: bytes, file_format: str) -> pd.DataFrame:
        if file_format == 'csv':
            return pd.read_csv(io.BytesIO(data))
        elif file_format == 'xlsx':
            return pd.read_excel(io.BytesIO(data), engine='openpyxl')
        raise ValueError(f"Unsupported file format: {file_format}")

    @abstractmethod
    def train_and_evaluate(self, X, y):
        pass

    def calculate_additional_metrics(self, y_test, predictions, binary_threshold=0.5):
        if len(np.unique(y_test)) == 2: 
            binary_preds = (predictions >= binary_threshold).astype(int)
            precision = precision_score(y_test, binary_preds)
            recall = recall_score(y_test, binary_preds)
            f1 = f1_score(y_test, binary_preds)
            accuracy = accuracy_score(y_test, binary_preds)
            specificity = recall_score(y_test, binary_preds, pos_label=0)
            auc = roc_auc_score(y_test, predictions)
            log_loss_val = log_loss(y_test, predictions)
            mcc = matthews_corrcoef(y_test, binary_preds)
            kappa = cohen_kappa_score(y_test, binary_preds)
            balanced_acc = balanced_accuracy_score(y_test, binary_preds)
            g_mean = np.sqrt(recall * specificity)
            conf_matrix = confusion_matrix(y_test, binary_preds).tolist()
        else:
            precision = recall = f1 = accuracy = specificity = auc = log_loss_val = mcc = kappa = balanced_acc = g_mean = None
            conf_matrix = None

        return {
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1,
            "Accuracy": accuracy,
            "Specificity": specificity,
            "PR-AUC": auc,
            "Log Loss": log_loss_val,
            "MCC": mcc,
            "Cohen's Kappa": kappa,
            "Balanced Accuracy": balanced_acc,
            "G-Mean": g_mean,
            "Confusion Matrix": conf_matrix,
        }


class LinearRegression(IModelStrategy):
    def __init__(self):
        self.model = SklearnLinearRegression()
        self.results = {}

    def train_and_evaluate(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if not all(is_numeric_dtype(X[col]) for col in X.columns):
            raise ValueError("Dataset contains non-numeric values. Please preprocess your data.")
        if X.isnull().values.any() or y.isnull().values.any():
            raise ValueError("Dataset contains missing values. Please preprocess your data.")

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)

        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        adjusted_r2 = 1 - (1 - r2) * ((X_test.shape[0] - 1) / (X_test.shape[0] - X_test.shape[1] - 1))
        standard_error = np.sqrt(mse)

        residuals = y_test - predictions

        n = X_train.shape[0]
        p = X_train.shape[1]
        ss_total = np.sum((y_test - np.mean(y_test)) ** 2)
        ss_regression = np.sum((predictions - np.mean(y_test)) ** 2)
        ss_error = ss_total - ss_regression
        df_regression = p
        df_error = n - p - 1
        ms_regression = ss_regression / df_regression
        ms_error = ss_error / df_error
        f_statistic = ms_regression / ms_error
        p_value = 1 - f.cdf(f_statistic, df_regression, df_error)

        additional_metrics = self.calculate_additional_metrics(y_test, predictions)

        self.results = {
            "MSE": mse,
            "R2": r2,
            "Adjusted R2": adjusted_r2,
            "Standard Error": standard_error,
            "Residuals": residuals.tolist(),
            "Predictions": predictions.tolist(),
            "Actuals": y_test.tolist(),
            "ANOVA": {
                "df_regression": df_regression,
                "df_error": df_error,
                "F": f_statistic,
                "p": p_value,
            },
            **additional_metrics,
        }
        return self.results


class PolynomialRegression(IModelStrategy):
    def __init__(self, degree=2):
        self.degree = degree
        self.model = SklearnLinearRegression()
        self.poly_features = PolynomialFeatures(degree=self.degree)
        self.results = {}

    def train_and_evaluate(self, X, y):
        X_poly = self.poly_features.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)

        if not all(is_numeric_dtype(X[col]) for col in X.columns):
            raise ValueError("Dataset contains non-numeric values. Please preprocess your data.")
        if X.isnull().values.any() or y.isnull().values.any():
            raise ValueError("Dataset contains missing values. Please preprocess your data.")

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)

        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        adjusted_r2 = 1 - (1 - r2) * ((X_test.shape[0] - 1) / (X_test.shape[0] - X_test.shape[1] - 1))
        standard_error = np.sqrt(mse)

        residuals = y_test - predictions

        additional_metrics = self.calculate_additional_metrics(y_test, predictions)

        self.results = {
            "MSE": mse,
            "R2": r2,
            "Adjusted R2": adjusted_r2,
            "Standard Error": standard_error,
            "Residuals": residuals.tolist(),
            "Predictions": predictions.tolist(),
            "Actuals": y_test.tolist(),
            **additional_metrics,
        }
        return self.results


class LassoRegression(IModelStrategy):
    def __init__(self, alpha=1.0):
        self.model = Lasso(alpha=alpha)
        self.alpha = alpha
        self.results = {}

    def train_and_evaluate(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if not all(is_numeric_dtype(X[col]) for col in X.columns):
            raise ValueError("Dataset contains non-numeric values. Please preprocess your data.")
        if X.isnull().values.any() or y.isnull().values.any():
            raise ValueError("Dataset contains missing values. Please preprocess your data.")

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)

        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        adjusted_r2 = 1 - (1 - r2) * ((X_test.shape[0] - 1) / (X_test.shape[0] - X_test.shape[1] - 1))
        standard_error = np.sqrt(mse)

        residuals = y_test - predictions

        additional_metrics = self.calculate_additional_metrics(y_test, predictions)

        self.results = {
            "MSE": mse,
            "R2": r2,
            "Adjusted R2": adjusted_r2,
            "Standard Error": standard_error,
            "Residuals": residuals.tolist(),
            "Predictions": predictions.tolist(),
            "Actuals": y_test.tolist(),
            **additional_metrics,
        }
        return self.results


class NaiveBayes(IModelStrategy):
    def __init__(self):
        super().__init__()
        self.model = GaussianNB()
        self.results = {}

    def train_and_evaluate(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        probabilities = self.model.predict_proba(X_test)[:, 1] if len(np.unique(y)) == 2 else None

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
        recall = recall_score(y_test, predictions, average='weighted')
        f1 = f1_score(y_test, predictions, average='weighted')
        conf_matrix = confusion_matrix(y_test, predictions).tolist()

        auc = roc_auc_score(y_test, probabilities) if probabilities is not None else None
        log_loss_val = log_loss(y_test, probabilities) if probabilities is not None else None
        mcc = matthews_corrcoef(y_test, predictions)
        kappa = cohen_kappa_score(y_test, predictions)
        balanced_acc = balanced_accuracy_score(y_test, predictions)

        self.results = {
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1,
            "Confusion Matrix": conf_matrix,
            "PR-AUC": auc,
            "Log Loss": log_loss_val,
            "MCC": mcc,
            "Cohen's Kappa": kappa,
            "Balanced Accuracy": balanced_acc,
        }
        return self.results


class LogisticRegression(IModelStrategy):
    def __init__(self):
        self.model = SklearnLogisticRegression(max_iter=1000)

    def train_and_evaluate(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        probabilities = self.model.predict_proba(X_test)[:, 1] if len(np.unique(y)) == 2 else None

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
        recall = recall_score(y_test, predictions, average='weighted')
        f1 = f1_score(y_test, predictions, average='weighted')
        conf_matrix = confusion_matrix(y_test, predictions).tolist()

        roc_curve_data, pr_curve_data = None, None
        if len(np.unique(y)) == 2:
            fpr, tpr, _ = roc_curve(y_test, probabilities)
            precision_vals, recall_vals, _ = precision_recall_curve(y_test, probabilities)
            roc_curve_data = {'fpr': fpr, 'tpr': tpr}
            pr_curve_data = {'precision': precision_vals, 'recall': recall_vals}

        return {
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1,
            "Confusion Matrix": conf_matrix,
            "ROC Curve Data": roc_curve_data,
            "PR Curve Data": pr_curve_data,
        }


class KNearestNeighbors(IModelStrategy):
    def __init__(self, n_neighbors=5):
        super().__init__()
        self.n_neighbors = n_neighbors
        self.model = KNeighborsClassifier(n_neighbors=self.n_neighbors)
        self.results = {}

    def train_and_evaluate(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if not all(is_numeric_dtype(X[col]) for col in X.columns):
            raise ValueError("Dataset contains non-numeric values. Please preprocess your data.")
        if X.isnull().values.any() or y.isnull().values.any():
            raise ValueError("Dataset contains missing values. Please preprocess your data.")

        self.model = KNeighborsClassifier(n_neighbors=self.n_neighbors)
        self.model.fit(X_train, y_train)

        predictions = self.model.predict(X_test)
        probabilities = self.model.predict_proba(X_test)[:, 1] if len(np.unique(y)) == 2 else None

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
        recall = recall_score(y_test, predictions, average='weighted')
        f1 = f1_score(y_test, predictions, average='weighted')
        conf_matrix = confusion_matrix(y_test, predictions).tolist()

        auc = roc_auc_score(y_test, probabilities) if probabilities is not None else None
        log_loss_val = log_loss(y_test, probabilities) if probabilities is not None else None
        mcc = matthews_corrcoef(y_test, predictions)
        kappa = cohen_kappa_score(y_test, predictions)
        balanced_acc = balanced_accuracy_score(y_test, predictions)

        self.results = {
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1,
            "Confusion Matrix": conf_matrix,
            "PR-AUC": auc,
            "Log Loss": log_loss_val,
            "MCC": mcc,
            "Cohen's Kappa": kappa,
            "Balanced Accuracy": balanced_acc,
        }
        return self.results


class SupportVectorClassifier(IModelStrategy):
    def __init__(self, kernel="linear", C=1.0):
        super().__init__()
        self.model = SVC(kernel=kernel, C=C, probability=True)
        self.kernel = kernel
        self.C = C
        self.results = {}

    def train_and_evaluate(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        probabilities = self.model.predict_proba(X_test)[:, 1] if len(np.unique(y)) == 2 else None

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
        recall = recall_score(y_test, predictions, average='weighted')
        f1 = f1_score(y_test, predictions, average='weighted')
        conf_matrix = confusion_matrix(y_test, predictions).tolist()

        auc = roc_auc_score(y_test, probabilities) if probabilities is not None else None
        log_loss_val = log_loss(y_test, probabilities) if probabilities is not None else None
        mcc = matthews_corrcoef(y_test, predictions)
        kappa = cohen_kappa_score(y_test, predictions)
        balanced_acc = balanced_accuracy_score(y_test, predictions)

        self.results = {
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1,
            "Confusion Matrix": conf_matrix,
            "PR-AUC": auc,
            "Log Loss": log_loss_val,
            "MCC": mcc,
            "Cohen's Kappa": kappa,
            "Balanced Accuracy": balanced_acc,
        }
        return self.results


class DecisionTreeClassifierModel(IModelStrategy):
    def __init__(self, max_depth=None, min_samples_split=2, min_samples_leaf=1):
        super().__init__()
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.model = DecisionTreeClassifier(
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf
        )
        self.results = {}

    def train_and_evaluate(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if not all(is_numeric_dtype(X[col]) for col in X.columns):
            raise ValueError("Dataset contains non-numeric values. Please preprocess your data.")
        if X.isnull().values.any() or y.isnull().values.any():
            raise ValueError("Dataset contains missing values. Please preprocess your data.")

        self.model.fit(X_train, y_train)

        predictions = self.model.predict(X_test)
        probabilities = self.model.predict_proba(X_test)[:, 1] if len(np.unique(y)) == 2 else None

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
        recall = recall_score(y_test, predictions, average='weighted')
        f1 = f1_score(y_test, predictions, average='weighted')
        conf_matrix = confusion_matrix(y_test, predictions).tolist()

        auc = roc_auc_score(y_test, probabilities) if probabilities is not None else None
        log_loss_val = log_loss(y_test, probabilities) if probabilities is not None else None
        mcc = matthews_corrcoef(y_test, predictions)
        kappa = cohen_kappa_score(y_test, predictions)
        balanced_acc = balanced_accuracy_score(y_test, predictions)

        self.results = {
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1,
            "Confusion Matrix": conf_matrix,
            "PR-AUC": auc,
            "Log Loss": log_loss_val,
            "MCC": mcc,
            "Cohen's Kappa": kappa,
            "Balanced Accuracy": balanced_acc,
        }
        return self.results


class RandomForestClassifierModel(IModelStrategy):
    def __init__(self, n_estimators=100, max_depth=None):
        super().__init__()
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=42
        )
        self.results = {}

    def train_and_evaluate(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        probabilities = self.model.predict_proba(X_test)[:, 1] if len(np.unique(y)) == 2 else None

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
        recall = recall_score(y_test, predictions, average='weighted')
        f1 = f1_score(y_test, predictions, average='weighted')
        conf_matrix = confusion_matrix(y_test, predictions).tolist()

        auc = roc_auc_score(y_test, probabilities) if probabilities is not None else None
        log_loss_val = log_loss(y_test, probabilities) if probabilities is not None else None
        mcc = matthews_corrcoef(y_test, predictions)
        kappa = cohen_kappa_score(y_test, predictions)
        balanced_acc = balanced_accuracy_score(y_test, predictions)

        self.results = {
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1,
            "Confusion Matrix": conf_matrix,
            "PR-AUC": auc,
            "Log Loss": log_loss_val,
            "MCC": mcc,
            "Cohen's Kappa": kappa,
            "Balanced Accuracy": balanced_acc,
        }
        return self.results


class SupportVectorRegression(IModelStrategy):
    def __init__(self, kernel="rbf", C=1.0, epsilon=0.1):
        super().__init__()
        self.kernel = kernel
        self.C = C
        self.epsilon = epsilon
        self.model = SVR(kernel=self.kernel, C=self.C, epsilon=self.epsilon)
        self.results = {}

    def train_and_evaluate(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)

        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        adjusted_r2 = 1 - (1 - r2) * ((X_test.shape[0] - 1) / (X_test.shape[0] - X_test.shape[1] - 1))
        standard_error = np.sqrt(mse)

        residuals = y_test - predictions

        self.results = {
            "MSE": mse,
            "R2": r2,
            "Adjusted R2": adjusted_r2,
            "Standard Error": standard_error,
            "Residuals": residuals.tolist(),
            "Predictions": predictions.tolist(),
            "Actuals": y_test.tolist(),
        }
        return self.results


class DecisionTreeRegressorModel(IModelStrategy):
    def __init__(self, max_depth=None, min_samples_split=2, min_samples_leaf=1):
        super().__init__()
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.model = DecisionTreeRegressor(
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            random_state=42
        )
        self.results = {}

    def train_and_evaluate(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)

        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        adjusted_r2 = 1 - (1 - r2) * ((X_test.shape[0] - 1) / (X_test.shape[0] - X_test.shape[1] - 1))
        standard_error = np.sqrt(mse)

        residuals = y_test - predictions

        self.results = {
            "MSE": mse,
            "R2": r2,
            "Adjusted R2": adjusted_r2,
            "Standard Error": standard_error,
            "Residuals": residuals.tolist(),
            "Predictions": predictions.tolist(),
            "Actuals": y_test.tolist(),
        }
        return self.results


class ModelContext:
    def __init__(self):
        self.strategy = None

    def set_strategy(self, strategy: IModelStrategy):
        self.strategy = strategy

    def train_and_evaluate(self, X, y):
        if not self.strategy:
            raise ValueError("No strategy set for model.")
        return self.strategy.train_and_evaluate(X, y)

def preprocess_data(data):
    with st.spinner("Preprocessing the data..."):
        data = data.dropna()

        for col in data.columns:
            if not is_numeric_dtype(data[col]):
                data[col] = data[col].astype('category').cat.codes

        st.session_state.preprocessed_data = data

def reset_results_on_new_dataset():
    if "results" in st.session_state:
        del st.session_state["results"]
    if "preprocessed_data" in st.session_state:
        del st.session_state["preprocessed_data"]
    if "df_for_modeling" in st.session_state:
        del st.session_state["df_for_modeling"]
    if "dataset_name_for_modeling" in st.session_state:
        del st.session_state["dataset_name_for_modeling"]

def models_page():
    load_css()
    st.header("Model Training and Evaluation", divider='violet')

    if 'model_context' not in st.session_state:
        st.session_state.model_context = ModelContext()
    if 'df_for_modeling' not in st.session_state:
        st.warning("No dataset available. Ensure a dataset is loaded.")
        return

    data = st.session_state.df_for_modeling


    if isinstance(data, bytes):
        try:
            file_format = st.session_state.get("dataset_file_format", "csv")
            if file_format == "csv":
                data = pd.read_csv(io.BytesIO(data))
            elif file_format == "xlsx":
                data = pd.read_excel(io.BytesIO(data), engine="openpyxl")
            else:
                st.error("Unsupported file format.")
                return
        except Exception as e:
            st.error(f"Error loading dataset: {e}")
            return

    if data.empty:
        st.error("The dataset is empty. Please load a valid dataset.")
        return


    dataset_name = st.session_state.dataset_name_for_modeling
    # with st.container(border=True):
    #     st.write(f"Visualizing Dataset: {dataset_name}")
    with st.expander(f"Dataset: {dataset_name}"):
        st.dataframe(data)

    with st.container(border=True):
        left_col, _, right_col = st.columns([0.20, 0.02, 0.78])

        with left_col:
            task_type = st.selectbox("Select Task Type", ["Select", "Classification", "Regression"])
            if task_type == "Select":
                st.warning("Please select a task type to proceed.")
                return

            if task_type == "Regression":
                model_type = st.selectbox(
                    "Choose Model", ["Select", "Linear Regression", "Polynomial Regression", "Lasso Regression", "Support Vector Regression (SVR)", "Decision Tree Regressor"]
                )

            elif task_type == "Classification":
                model_type = st.selectbox(
                    "Choose Model", [
                        "Select", 
                        "Naive Bayes", 
                        "Logistic Regression", 
                        "K-Nearest Neighbors (KNN)", 
                        "Support Vector Classifier (SVC)", 
                        "Decision Tree Classifier", 
                        "Random Forest Classifier"
                    ]
                )

            if model_type == "Select":
                st.warning("Please select a model to proceed.")
                return

            if 'preprocessed_data' not in st.session_state:
                if st.button("Preprocess Dataset"):
                    preprocess_data(data)

            if 'preprocessed_data' not in st.session_state:
                st.warning("Please preprocess the dataset to continue.")
                return

            preprocessed_data = st.session_state.preprocessed_data
            if task_type == "Regression":
                potential_targets = [
                    col for col in preprocessed_data.columns
                    if is_numeric_dtype(preprocessed_data[col]) and preprocessed_data[col].nunique() > 10
                ]
            elif task_type == "Classification":
                potential_targets = [
                    col for col in preprocessed_data.columns
                    if preprocessed_data[col].nunique() <= 10
                ]

            if not potential_targets:
                st.error("No suitable target variables found for the selected task type.")
                return

            target_col = st.selectbox("Select Target Variable", ["Select"] + potential_targets, key="target_col")
            if target_col == "Select":
                st.warning("Please select a target variable to proceed.")
                return

            if model_type == "Polynomial Regression":
                polynomial_degree = st.slider(
                    "Select Polynomial Degree", 2, 5, st.session_state.get("polynomial_degree", 2), key="polynomial_degree"
                )

            if model_type == "K-Nearest Neighbors (KNN)":
                knn_neighbors = st.number_input(
                    "Select Number of Neighbors (K)",
                    min_value=1,
                    max_value=50,
                    value=5,
                    step=1,
                    key="knn_neighbors"
                )

            if model_type == "Decision Tree Classifier":
                max_depth = st.number_input(
                    "Max Depth (None for unlimited)", min_value=1, value=st.session_state.get("max_depth", None), key="max_depth"
                )
            
                min_samples_split = st.number_input(
                    "Min Samples Split", min_value=2, value=st.session_state.get("min_samples_split", 2), key="min_samples_split"
                )
            
                min_samples_leaf = st.number_input(
                    "Min Samples Leaf", min_value=1, value=st.session_state.get("min_samples_leaf", 1), key="min_samples_leaf"
                )

            if model_type == "Lasso Regression":
                alpha_value = st.slider(
                    "Select Alpha Value", 0.01, 10.0, st.session_state.get("alpha_value", 1.0), step=0.01, key="alpha_value"
                )

            if model_type == "Support Vector Classifier (SVC)":
                svc_kernel = st.selectbox(
                    "Select Kernel for SVC",
                    ["poly", "rbf", "linear", "sigmoid"],
                    key="svc_kernel"
                )

                svc_C = st.slider(
                    "Select Regularization Parameter (C)",
                    0.01, 10.0, st.session_state.get("svc_C", 1.0), step=0.01, key="svc_C"
                )

            if model_type == "Random Forest Classifier":
                n_estimators = st.slider(
                    "Select Number of Trees (n_estimators)",
                    10, 500, st.session_state.get("n_estimators", 100), step=10, key="n_estimators"
                )
            
                max_depth = st.slider(
                    "Select Maximum Depth of Trees",
                    1, 50, st.session_state.get("max_depth", 50), step=1, key="max_depth"
                )

            if model_type == "Support Vector Regression (SVR)":
                svr_kernel = st.selectbox(
                    "Select Kernel for SVR",
                    ["linear", "poly", "rbf", "sigmoid"],
                    key="svr_kernel"
                )
            
                svr_C = st.slider(
                    "Select Regularization Parameter (C)",
                    0.01, 10.0, st.session_state.get("svr_C", 1.0), step=0.01, key="svr_C"
                )
            
                svr_epsilon = st.slider(
                    "Select Epsilon (Tolerance Margin)",
                    0.01, 1.0, st.session_state.get("svr_epsilon", 0.1), step=0.01, key="svr_epsilon"
                )

            if model_type == "Decision Tree Regressor":
                dt_max_depth = st.slider(
                    "Select Maximum Depth",
                    1, 50, st.session_state.get("dt_max_depth", 10), key="dt_max_depth"
                )
            
                dt_min_samples_split = st.slider(
                    "Select Minimum Samples Split",
                    2, 20, st.session_state.get("dt_min_samples_split", 2), key="dt_min_samples_split"
                )
            
                dt_min_samples_leaf = st.slider(
                    "Select Minimum Samples per Leaf",
                    1, 20, st.session_state.get("dt_min_samples_leaf", 1), key="dt_min_samples_leaf"
                )


            if st.button("Run Model"):
                X = preprocessed_data.drop(columns=[target_col])
                y = preprocessed_data[target_col]
            
                try:
                    if model_type == "Linear Regression":
                        st.session_state.model_context.set_strategy(LinearRegression())
                    elif model_type == "Polynomial Regression":
                        st.session_state.model_context.set_strategy(
                            PolynomialRegression(degree=st.session_state.polynomial_degree)
                        )
                    elif model_type == "Lasso Regression":
                        st.session_state.model_context.set_strategy(
                            LassoRegression(alpha=st.session_state.alpha_value)
                        )
                    elif model_type == "Naive Bayes":
                        st.session_state.model_context.set_strategy(NaiveBayes())
                    elif model_type == "Logistic Regression":
                        st.session_state.model_context.set_strategy(LogisticRegression())
                    elif model_type == "K-Nearest Neighbors (KNN)":
                        st.session_state.model_context.set_strategy(KNearestNeighbors(n_neighbors=st.session_state.knn_neighbors))
                    elif model_type == "Support Vector Classifier (SVC)":
                        st.session_state.model_context.set_strategy(
                            SupportVectorClassifier(kernel=st.session_state.svc_kernel, C=st.session_state.svc_C)
                        )
                    elif model_type == "Decision Tree Classifier":
                        st.session_state.model_context.set_strategy(
                            DecisionTreeClassifierModel(
                                max_depth=st.session_state.max_depth,
                                min_samples_split=st.session_state.min_samples_split,
                                min_samples_leaf=st.session_state.min_samples_leaf
                            )
                        )

                    elif model_type == "Random Forest Classifier":
                        st.session_state.model_context.set_strategy(
                            RandomForestClassifierModel(
                                n_estimators=st.session_state.n_estimators,
                                max_depth=st.session_state.max_depth,
                            )
                        )

                    elif model_type == "Support Vector Regression (SVR)":
                        st.session_state.model_context.set_strategy(
                            SupportVectorRegression(kernel=svr_kernel, C=svr_C, epsilon=svr_epsilon)
                        )

                    elif model_type == "Decision Tree Regressor":
                        st.session_state.model_context.set_strategy(
                            DecisionTreeRegressorModel(
                                max_depth=dt_max_depth,
                                min_samples_split=dt_min_samples_split,
                                min_samples_leaf=dt_min_samples_leaf
                            )
                        )
                    

                    results = st.session_state.model_context.train_and_evaluate(X, y)
            
                    st.session_state.results = results
            
                    st.success(f"Model '{model_type}' has been trained and evaluated successfully!")
            
                except ValueError as e:
                    st.error(f"Error during model training and evaluation: {e}")
            

        with right_col:
            if "results" in st.session_state:
                results = st.session_state.results
        
                is_classification = "Precision" in results and results["Precision"] is not None
                is_regression = "MSE" in results and results["MSE"] is not None
        
                st.write("##### Metrics")
                if is_regression:
                    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                    with metrics_col1:
                        st.metric("MSE", f"{results['MSE']:.2f}")
                    with metrics_col2:
                        st.metric("R²", f"{results['R2']:.2f}")
                    with metrics_col3:
                        st.metric("Adjusted R²", f"{results['Adjusted R2']:.2f}")
                    with metrics_col4:
                        st.metric("Standard Error", f"{results['Standard Error']:.2f}")
        
                if is_classification:
                    st.write("##### Classification Metrics")
                    classification_col1, classification_col2, classification_col3, classification_col4 = st.columns(4)
                    with classification_col1:
                        st.metric("Precision", f"{results['Precision']:.2f}")
                    with classification_col2:
                        st.metric("Recall", f"{results['Recall']:.2f}")
                    with classification_col3:
                        st.metric("F1-Score", f"{results['F1-Score']:.2f}")
                    with classification_col4:
                        st.metric("Accuracy", f"{results['Accuracy']:.2f}")
        
                    classification_col5, classification_col6, classification_col7, classification_col8 = st.columns(4)
                    with classification_col5:
                        specificity = results.get('Specificity')
                        st.metric("Specificity", f"{specificity:.2f}" if specificity is not None else "N/A")
                    with classification_col6:
                        pr_auc = results.get('PR-AUC')
                        st.metric("PR-AUC", f"{pr_auc:.2f}" if pr_auc is not None else "N/A")
                    with classification_col7:
                        log_loss_val = results.get('Log Loss')
                        st.metric("Log Loss", f"{log_loss_val:.2f}" if log_loss_val is not None else "N/A")
                    with classification_col8:
                        mcc = results.get('MCC')
                        st.metric("MCC", f"{mcc:.2f}" if mcc is not None else "N/A")
        
                    classification_col9, classification_col10, classification_col11 = st.columns(3)
                    with classification_col9:
                        cohen_kappa = results.get("Cohen's Kappa")
                        st.metric("Cohen's Kappa", f"{cohen_kappa:.2f}" if cohen_kappa is not None else "N/A")
                    with classification_col10:
                        balanced_accuracy = results.get('Balanced Accuracy')
                        st.metric("Balanced Accuracy", f"{balanced_accuracy:.2f}" if balanced_accuracy is not None else "N/A")
                    with classification_col11:
                        g_mean = results.get('G-Mean')
                        st.metric("G-Mean", f"{g_mean:.2f}" if g_mean is not None else "N/A")
        
                    if "Confusion Matrix" in results and results["Confusion Matrix"] is not None:
                        confusion_matrix = results["Confusion Matrix"]

                        cm_col1, cm_col2 = st.columns(2)

                        with cm_col1:
                            st.write("##### Confusion Matrix Table")
                            confusion_matrix_df = pd.DataFrame(
                                confusion_matrix,
                                columns=[f"Predicted {i}" for i in range(len(confusion_matrix))],
                                index=[f"Actual {i}" for i in range(len(confusion_matrix))]
                            )
                            st.dataframe(confusion_matrix_df)

                        with cm_col2:
                            st.write("##### Confusion Matrix Heatmap")
                            confusion_matrix_fig = px.imshow(
                                confusion_matrix, text_auto=True,
                                title="Confusion Matrix Heatmap",
                                labels=dict(x="Predicted", y="Actual")
                            )
                            st.plotly_chart(confusion_matrix_fig)

                    classification_vis_col1, classification_vis_col2 = st.columns(2)

                    with classification_vis_col1:

                        # ROC Curve
                        if "ROC Curve Data" in results and results["ROC Curve Data"] is not None:
                            roc_data = results["ROC Curve Data"]
                            if "fpr" in roc_data and "tpr" in roc_data:
                                roc_fig = px.area(
                                    x=roc_data["fpr"], y=roc_data["tpr"],
                                    title="ROC Curve",
                                    labels={'x': 'False Positive Rate', 'y': 'True Positive Rate'}
                                )
                                roc_fig.add_shape(
                                    type='line', line=dict(dash='dash'),
                                    x0=0, x1=1, y0=0, y1=1
                                )
                                st.plotly_chart(roc_fig)

                    with classification_vis_col2:
                        if "PR Curve Data" in results and results["PR Curve Data"] is not None:
                            pr_data = results["PR Curve Data"]
                            if "recall" in pr_data and "precision" in pr_data:
                                pr_fig = px.line(
                                    x=pr_data["recall"], y=pr_data["precision"],
                                    title="Precision-Recall Curve",
                                    labels={'x': 'Recall', 'y': 'Precision'}
                                )
                                st.plotly_chart(pr_fig)

                    if "Predictions" in results:
                        predictions = results["Predictions"]
                        actuals = results["Actuals"]
                        class_dist_df = pd.DataFrame({
                            "Class": ["Actual Negative", "Actual Positive", "Predicted Negative", "Predicted Positive"],
                            "Count": [
                                np.sum(actuals == 0), np.sum(actuals == 1),
                                np.sum(np.array(predictions) < 0.5), np.sum(np.array(predictions) >= 0.5)
                            ]
                        })
                        class_dist_fig = px.bar(
                            class_dist_df, x="Class", y="Count",
                            title="Class Distribution",
                            labels={'Count': 'Number of Instances'}
                        )
                        st.plotly_chart(class_dist_fig)

                if is_regression:
                    residuals = results.get("Residuals")
                    predictions = results["Predictions"]
                    actuals = results["Actuals"]
        
                    vis_row1_col1, vis_row1_col2, vis_row1_col3 = st.columns(3)
        
                    with vis_row1_col1:
                        scatter_fig = px.scatter(
                            x=actuals, y=predictions,
                            labels={'x': 'Actual', 'y': 'Predicted'},
                            title="Actual vs. Predicted"
                        )
                        scatter_fig.add_trace(go.Scatter(x=actuals, y=actuals, mode='lines', name='Ideal Fit'))
                        st.plotly_chart(scatter_fig)
        
                    with vis_row1_col2:
                        if residuals:
                            residual_actual_fig = px.scatter(
                                x=actuals, y=residuals,
                                labels={'x': 'Actual Values', 'y': 'Residuals'},
                                title="Residuals vs. Actual Values"
                            )
                            residual_actual_fig.add_hline(y=0, line_dash="dash", line_color="red")
                            st.plotly_chart(residual_actual_fig)
        
                    with vis_row1_col3:
                        prediction_dist_fig = px.histogram(
                            predictions, nbins=30, title="Prediction Distribution",
                            labels={'value': 'Predictions'}
                        )
                        prediction_dist_fig.add_trace(go.Histogram(x=actuals, nbinsx=30, name="Actual"))
                        st.plotly_chart(prediction_dist_fig)
        
                    vis_row2_col1, vis_row2_col2, vis_row2_col3 = st.columns(3)
        
                    with vis_row2_col1:
                        box_plot_fig = px.box(
                            pd.DataFrame({"Actual": actuals, "Predicted": predictions}),
                            title="Box Plot of Actuals and Predictions"
                        )
                        st.plotly_chart(box_plot_fig)
        
                    with vis_row2_col2:
                        if residuals:
                            residual_dist_fig = px.histogram(
                                residuals, nbins=30, title="Residual Distribution", marginal="box",
                                labels={'value': 'Residuals'}
                            )
                            st.plotly_chart(residual_dist_fig)
        
                    with vis_row2_col3:
                        if isinstance(st.session_state.model_context.strategy, LassoRegression):
                            feature_importance = pd.DataFrame({
                                "Feature": st.session_state.preprocessed_data.drop(columns=[st.session_state.target_col]).columns,
                                "Importance": st.session_state.model_context.strategy.model.coef_
                            }).sort_values(by="Importance", ascending=False)
        
                            feature_importance_fig = px.bar(
                                feature_importance, x="Feature", y="Importance",
                                title="Feature Importance (Lasso Regression)"
                            )
                            st.plotly_chart(feature_importance_fig)
        
                if is_regression:
                    st.write("###### Predictions Table")
                    predictions_df = pd.DataFrame({
                        "Actual": actuals,
                        "Predicted": predictions,
                        "Residual": residuals
                    })
                    st.dataframe(predictions_df, use_container_width=True)

models_page()