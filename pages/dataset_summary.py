import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def load_css():
    with open('static/style.css') as f:
        css_code = f.read()
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)


def calculate_memory_usage(df):
    return df.memory_usage(deep=True).sum()


def is_hashable(val):
    try:
        hash(val)
    except TypeError:
        return False
    return True


def make_hashable(df):
    return df.applymap(lambda x: tuple(x) if isinstance(x, list) else x)


def generate_dataset_description(df):
    num_variables = df.shape[1]
    num_observations = df.shape[0]
    numerical_features = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = df.select_dtypes(include=['object']).columns.tolist()
    missing_cells = df.isnull().sum().sum()
    
    # Convert non-hashable types to hashable types
    hashable_df = make_hashable(df)
    duplicate_rows = hashable_df.duplicated().sum()

    description = f"""
    The dataset contains {num_variables} variables and {num_observations} observations.
    There are {len(numerical_features)} numerical features and {len(categorical_features)} categorical features.
    The dataset has {missing_cells} missing cells and {duplicate_rows} duplicate rows.
    This dataset can be used for various data analysis and machine learning tasks, providing opportunities to explore and model the data in depth.
    With its mix of numerical and categorical data, it allows for comprehensive statistical analyses and predictive modeling.
    Additionally, handling missing data and duplicate rows can help improve data quality and model performance.
    """

    return description


class DatasetSummary:
    @staticmethod
    def display_summary(df, dataset_name):
        # Generate and display dataset description
        description = generate_dataset_description(df)

        with st.expander("Dataset"):
            st.write(f"### Dataset: {dataset_name}")
            st.write(description)

        # Identify features
        categorical_features = df.select_dtypes(include=['object']).columns.tolist()
        numerical_features = df.select_dtypes(include=[np.number]).columns.tolist()

        # Calculate warnings
        warnings = []
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                warnings.append((col, f"{df[col].isnull().sum()} ({(df[col].isnull().sum() / df.shape[0]) * 100:.1f}%) missing values", "missing"))
            if is_hashable(df[col].iloc[0]) and df[col].nunique() / df.shape[0] > 0.5:
                warnings.append((col, f"high cardinality: {df[col].nunique()} distinct values", "warning"))
            if df[col].dtype in [np.number] and df[col].skew() > 1:
                warnings.append((col, f"highly skewed (γ1 = {df[col].skew():.2f})", "skewed"))

        # Overview Section
        with st.container(border=True):
            st.header("Overview")

            overview_tab1, overview_tab2, overview_tab3, overview_tab4 = st.tabs(
                ["Dataset Info", "Variable Types", "Variables", f"Warnings ({len(warnings)})"])

            with overview_tab1:
                st.write("##### Dataset Info")
                num_variables = df.shape[1]
                num_observations = df.shape[0]
                missing_cells = df.isnull().sum().sum()
                hashable_df = make_hashable(df)
                duplicate_rows = hashable_df[hashable_df.duplicated()].shape[0]
                total_size = calculate_memory_usage(df)
                avg_record_size = total_size / num_observations

                row1_col1, row1_col2 = st.columns(2)
                row2_col1, row2_col2 = st.columns(2)
                row3_col1, row3_col2 = st.columns(2)

                with row1_col1:
                    st.metric(label="Number of Variables", value=num_variables)
                with row1_col2:
                    st.metric(label="Number of Observations", value=num_observations)
                
                missing_delta_color = "off" if missing_cells == 0 else "inverse" if (missing_cells / (num_variables * num_observations)) * 100 > 1 else "normal"
                with row2_col1:
                    st.metric(label="Missing Cells", value=missing_cells, delta=f"{(missing_cells / (num_variables * num_observations)) * 100:.1f}%", delta_color=missing_delta_color)
                
                duplicate_delta_color = "off" if duplicate_rows == 0 else "inverse" if (duplicate_rows / num_observations) * 100 > 1 else "normal"
                with row2_col2:
                    st.metric(label="Duplicate Rows", value=duplicate_rows, delta=f"{(duplicate_rows / num_observations) * 100:.1f}%", delta_color=duplicate_delta_color)
                
                with row3_col1:
                    st.metric(label="Total Size in Memory", value=f"{total_size / (1024 ** 2):.1f} MB")
                with row3_col2:
                    st.metric(label="Average Record Size in Memory", value=f"{avg_record_size:.1f} B")

            with overview_tab2:
                st.write("##### Variable Types")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Numerical", len(numerical_features))
                    st.metric("Categorical", len(categorical_features))
                    st.metric("Boolean", df.select_dtypes(include=['bool']).shape[1])
                with col2:
                    st.metric("Date", df.select_dtypes(include=['datetime']).shape[1])
                    st.metric("Text (Unique)", df.select_dtypes(include=['category']).shape[1])

            with overview_tab3:
                st.write("##### Variables")
                st.write(df.columns.tolist())

            with overview_tab4:
                st.write("##### Warnings")
                if warnings:
                    for warning in warnings:
                        col_name, message, warning_type = warning
                        if warning_type == "missing":
                            st.write(f"<span style='color: red;'>{col_name}</span> {message} <span style='background-color: #f0ad4e; color: white; padding: 2px 6px; border-radius: 4px;'>Missing</span>", unsafe_allow_html=True)
                        elif warning_type == "warning":
                            st.write(f"<span style='color: red;'>{col_name}</span> {message} <span style='background-color: rgb(255,0,0,0.7); color: white; padding: 2px 6px; border-radius: 4px;'>Warning</span>", unsafe_allow_html=True)
                        elif warning_type == "skewed":
                            st.write(f"<span style='color: red;'>{col_name}</span> {message} <span style='background-color: #5bc0de; color: white; padding: 2px 6px; border-radius: 4px;'>Skewed</span>", unsafe_allow_html=True)
                else:
                    st.write("No warnings")

        # Numerical Features Analysis
        with st.container(border=True):
            st.subheader("Numerical Features Analysis")
            num_tab1, num_tab2, num_tab3, num_tab4, num_tab5, num_tab6, num_tab7, num_tab8, num_tab9, num_tab10 = st.tabs([
                "Feature Names",
                "Missing Values",
                "Unique Values",
                "Most Frequent Values",
                "Data Types",
                "Memory Usage",
                "Basic Statistics",
                "Correlation Matrix",
                "Distribution",
                "Histograms & Box Plots"
            ])

            with num_tab1:
                st.write("##### Feature Names")
                st.write(numerical_features)

            with num_tab2:
                st.write("##### Missing Values")
                missing_tab1, missing_tab2 = st.tabs(["Table", "Visualization"])
                with missing_tab1:
                    missing_values = df[numerical_features].isnull().sum().reset_index()
                    missing_values.columns = ['Feature', 'Missing Values']
                    missing_values['Percentage'] = (missing_values['Missing Values'] / df.shape[0]) * 100
                    st.write(missing_values)
                with missing_tab2:
                    fig = px.bar(missing_values, x='Feature', y='Missing Values', title='Missing Values Count', color_discrete_sequence=["#9933FF"])
                    st.plotly_chart(fig, use_container_width=True)

            with num_tab3:
                st.write("##### Unique Values")
                unique_tab1, unique_tab2 = st.tabs(["Table", "Visualization"])
                with unique_tab1:
                    # Convert non-hashable types to strings
                    unique_values = df[numerical_features].applymap(lambda x: str(x) if not is_hashable(x) else x).nunique().reset_index()
                    unique_values.columns = ['Feature', 'Unique Values']
                    st.write(unique_values)
                with unique_tab2:
                    fig = px.bar(unique_values, x='Feature', y='Unique Values', title='Unique Values Count', color_discrete_sequence=["#9933FF"])
                    st.plotly_chart(fig, use_container_width=True)

            with num_tab4:
                st.write("##### Most Frequent Values")
                most_frequent_values = df[numerical_features].mode().iloc[0].reset_index()
                most_frequent_values.columns = ['Feature', 'Most Frequent Value']
                st.write(most_frequent_values)

            with num_tab5:
                st.write("##### Data Types")
                data_types = df[numerical_features].dtypes.reset_index()
                data_types.columns = ['Feature', 'Data Type']
                st.write(data_types)

            with num_tab6:
                st.write("##### Memory Usage")
                memory_tab1, memory_tab2 = st.tabs(["Table", "Visualization"])
                with memory_tab1:
                    memory_usage = df[numerical_features].memory_usage(deep=True).reset_index()
                    memory_usage.columns = ['Feature', 'Memory Usage (Bytes)']
                    st.write(memory_usage)
                with memory_tab2:
                    fig = px.bar(memory_usage, x='Feature', y='Memory Usage (Bytes)', title='Memory Usage', color_discrete_sequence=["#9933FF"])
                    st.plotly_chart(fig, use_container_width=True)

            with num_tab7:
                st.write("##### Basic Statistics")
                if not df[numerical_features].empty:
                    st.write(df[numerical_features].describe())
                else:
                    st.write("No numerical columns found or DataFrame is empty.")

            with num_tab8:
                st.write("##### Correlation Matrix")
                if len(numerical_features) > 1:
                    corr_matrix = df[numerical_features].corr()
                    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale="Viridis")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("Not enough numerical columns for correlation matrix.")

            with num_tab9:
                st.write("##### Distribution")
                skew_tab, kurtosis_tab = st.tabs(["Skewness", "Kurtosis"])
                with skew_tab:
                    for feature in numerical_features:
                        skewness = df[feature].skew()
                        st.write(f"**{feature}**: {skewness}")

                with kurtosis_tab:
                    for feature in numerical_features:
                        kurtosis = df[feature].kurtosis()
                        st.write(f"**{feature}**: {kurtosis}")

            with num_tab10:
                st.write("##### Histograms & Box Plots")
                feature_tabs = st.tabs(numerical_features)
                for feature, tab in zip(numerical_features, feature_tabs):
                    with tab:
                        st.write(f"### {feature}")
                        hist_fig = px.histogram(df, x=feature, nbins=30, marginal="box", title=f"Histogram and Box Plot for {feature}", color_discrete_sequence=["#9933FF"])
                        st.plotly_chart(hist_fig, use_container_width=True)

        # Categorical Features Analysis
        with st.container(border=True):
            st.subheader("Categorical Features Analysis")
            cat_tab1, cat_tab2, cat_tab3, cat_tab4, cat_tab5, cat_tab6, cat_tab7 = st.tabs([
                "Feature Names",
                "Missing Values",
                "Unique Values",
                "Value Counts",
                "Data Types",
                "Top Frequent Categories",
                "Top N Categories"
            ])

            with cat_tab1:
                st.write("##### Feature Names")
                st.write(categorical_features)

            with cat_tab2:
                st.write("##### Missing Values")
                missing_tab1, missing_tab2 = st.tabs(["Table", "Visualization"])
                with missing_tab1:
                    missing_values = df[categorical_features].isnull().sum().reset_index()
                    missing_values.columns = ['Feature', 'Missing Values']
                    missing_values['Percentage'] = (missing_values['Missing Values'] / df.shape[0]) * 100
                    st.write(missing_values)
                with missing_tab2:
                    fig = px.bar(missing_values, x='Feature', y='Missing Values', title='Missing Values Count', color_discrete_sequence=["#9933FF"])
                    st.plotly_chart(fig, use_container_width=True)

            with cat_tab3:
                st.write("##### Unique Values")
                unique_tab1, unique_tab2 = st.tabs(["Table", "Visualization"])
                with unique_tab1:
                    # Convert non-hashable types to strings
                    unique_values = df[categorical_features].applymap(lambda x: str(x) if not is_hashable(x) else x).nunique().reset_index()
                    unique_values.columns = ['Feature', 'Unique Values']
                    st.write(unique_values)
                with unique_tab2:
                    fig = px.bar(unique_values, x='Feature', y='Unique Values', title='Unique Values Count', color_discrete_sequence=["#9933FF"])
                    st.plotly_chart(fig, use_container_width=True)

            with cat_tab4:
                st.write("##### Value Counts")
                value_tabs = st.tabs(categorical_features)
                for feature, tab in zip(categorical_features, value_tabs):
                    with tab:
                        st.write(df[feature].value_counts())

            with cat_tab5:
                st.write("##### Data Types")
                data_types = df[categorical_features].dtypes.reset_index()
                data_types.columns = ['Feature', 'Data Type']
                st.write(data_types)

            with cat_tab6:
                st.write("##### Top Frequent Categories")
                for feature in categorical_features:
                    st.write(f"**{feature}**: {df[feature].value_counts().idxmax()} (Most Frequent)")

            with cat_tab7:
                st.write("##### Top N Categories")
                top_n = st.slider("Select Top N", min_value=1, max_value=20, value=5)
                feature_tabs = st.tabs(categorical_features)
                for feature, tab in zip(categorical_features, feature_tabs):
                    with tab:
                        st.write(f"### Top {top_n} Categories for {feature}")
                        value_counts = df[feature].value_counts().head(top_n)
                        value_counts = value_counts.reset_index()  # Reset index to get a DataFrame
                        value_counts.columns = ['Category', 'Count']  # Rename the columns for clarity
                        fig = px.bar(value_counts, x='Category', y='Count', title=f"Top {top_n} Categories for {feature}", color_discrete_sequence=["#9933FF"])
                        st.plotly_chart(fig, use_container_width=True)

        # Data Overview
        with st.container(border=True):
            st.subheader("Data Overview")

            tab1, tab2, tab3, tab4 = st.tabs(["Dataset Head", "Dataset Middle", "Dataset Footer", "Full DataFrame"])
            with tab1:
                st.write("##### Dataset Head")
                st.write(df.head())
            with tab2:
                st.write("##### Dataset Middle")
                st.write(df.iloc[len(df)//2:len(df)//2+5])
            with tab3:
                st.write("##### Dataset Footer")
                st.write(df.tail())
            with tab4:
                st.write("##### Full DataFrame")
                st.dataframe(df)


def dataset_summary_page():
    load_css()
    st.header('Dataset Summary', divider='violet')

    if 'df' in st.session_state and 'dataset_name' in st.session_state:
        df = st.session_state.df
        dataset_name = st.session_state.dataset_name

        DatasetSummary.display_summary(df, dataset_name)

        col1, col2 = st.columns([5.4, 1])
        with col1:
            if st.button("Back to Upload", key="back_to_upload"):
                st.session_state.uploaded = False
                st.switch_page("pages/dataset_upload.py")
        with col2:
            if st.button("Go to Preprocessing", key="go_to_preprocessing"):
                st.switch_page("pages/data_preprocessing.py")


dataset_summary_page()
