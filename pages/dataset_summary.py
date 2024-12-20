import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from dataset import Dataset  
import streamlit_antd_components as sac
import os


def load_css():
    """Load custom CSS to style the interface."""
    try:
        css_patht = os.path.join(os.path.dirname(__file__), "../static/style.css")
        with open(css_patht) as f:
            css_code = f.read()
        st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS file not found. Using default styles.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


class DatasetSummary:
    def __init__(self, dataset_id, dataset_name):
        """Initialize DatasetSummary with a Dataset instance, loading dataset by ID."""
        self.dataset_db = Dataset()  
        self.dataset_id = dataset_id
        self.dataset_name = dataset_name
        self.dataset = self.load_dataset()


    def load_dataset(self):
        """Load dataset from the database by dataset ID and convert it to a pandas DataFrame."""
        if 'user_id' not in st.session_state:
            st.error("User not logged in. Please log in to view datasets.")
            return None
    
        user_id = st.session_state['user_id']
        dataset_record = self.dataset_db.get_dataset_by_id(self.dataset_id, user_id)
    
        if dataset_record:
            dataset_data = dataset_record.data  # This is the binary data from the database
            file_format = dataset_record.file_format
    
            try:
                if file_format == 'csv':
                    df = Dataset.try_parsing_csv(io.BytesIO(dataset_data))  # Correctly pass dataset_data here
                    if df is None:
                        st.error("Failed to parse the CSV file. Please check the file format.")
                        return None
                elif file_format == 'xlsx' or file_format == 'xls':  # Handle both .xlsx and .xls
                    df = pd.read_excel(io.BytesIO(dataset_data), engine='openpyxl')  # Pass dataset_data
                    if df is None:
                        st.error("Failed to parse the Excel file. Please check the file format.")
                        return None
                else:
                    st.error("Unsupported file type")
                    return None
            except Exception as e:
                st.error(f"Error while loading dataset: {e}")
                return None
    
            return df
        else:
            st.error(f"Dataset with ID {self.dataset_id} not found.")
            return None

    def update_last_accessed(self):
        """Update the last accessed timestamp for the current dataset."""
        if 'user_id' not in st.session_state:
            st.error("User not logged in. Please log in to update datasets.")
            return
        user_id = st.session_state['user_id']
        self.dataset_db.update_last_accessed(self.dataset_id, user_id)


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
        """Converts lists and dicts in DataFrame cells to tuples so they are hashable."""
        def convert_to_hashable(val):
            if isinstance(val, list):
                return tuple(val)
            elif isinstance(val, dict):
                return tuple(sorted(val.items()))
            return val

        return df.applymap(convert_to_hashable)


    def display_summary(self):
        """Display the summary of the dataset."""
        df = self.dataset
        if df is None:
            st.error("No dataset to display summary.")
            return
        with st.expander(f"Data Overview {self.dataset_name}"):
            # st.dataframe(df)

            st.subheader("Data Overview")

            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Dataset Head", 
                "Dataset Middle", 
                "Dataset Footer", 
                "Full DataFrame", 
                "Interactive Exploration"
            ])
    
            with tab1:
                with st.spinner("loading Dataset Head ..."):
                    st.write("##### Dataset Head")
                    st.write(df.head())
    
            with tab2:
                with st.spinner("loading Dataset Middle ..."):
                    st.write("##### Dataset Middle")
                    st.write(df.iloc[len(df)//2:len(df)//2+5])
    
            with tab3:
                with st.spinner("loading Dataset Footer ..."):
                    st.write("##### Dataset Footer")
                    st.write(df.tail())
    
            with tab4:
                with st.spinner("loading Full DataFrame ..."):
                    st.write("##### Full DataFrame")
                    st.dataframe(df)
    
            with tab5:
                with st.spinner("loading Interactive Dataset Exploration ..."):
                    st.write("##### Interactive Dataset Exploration")
                    DatasetSummary.interactive_dataset_exploration(df)

        categorical_features = df.select_dtypes(include=['object']).columns.tolist()
        numerical_features = df.select_dtypes(include=[np.number]).columns.tolist()

        warnings = []
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                warnings.append((col, f"{df[col].isnull().sum()} ({(df[col].isnull().sum() / df.shape[0]) * 100:.1f}%) missing values", "missing"))
            if DatasetSummary.is_hashable(df[col].iloc[0]) and df[col].nunique() / df.shape[0] > 0.5:
                warnings.append((col, f"high cardinality: {df[col].nunique()} distinct values", "warning"))
            if df[col].dtype in [np.number] and df[col].skew() > 1:
                warnings.append((col, f"highly skewed (γ1 = {df[col].skew():.2f})", "skewed"))
        
       

        overview, dataqualityinsights = st.columns([0.40, 0.60])

        # overview, dataqualityinsights = st.columns(2)
        with overview:
            with st.container(border=True, height=610):
                st.write("### Overview")
        
                overview_tab1, overview_tab2, overview_tab3, overview_tab4, overview_tab5 = st.tabs([
                    "Dataset Info",
                    "Variable Types",
                    "Variables",
                    "Numerical & Categorical Features",
                    f"Warnings ({len(warnings)})"

                ])
        
                # Tab 1: Dataset Info
                with overview_tab1:
                    with st.spinner("loading ..."):
                        # Metrics
                        num_variables = df.shape[1]
                        num_observations = df.shape[0]
                        missing_cells = df.isnull().sum().sum()
                        hashable_df = DatasetSummary.make_hashable(df)
                        duplicate_rows = hashable_df[hashable_df.duplicated()].shape[0]
                        total_size = DatasetSummary.calculate_memory_usage(df)
                        avg_record_size = total_size / num_observations
            
                        numerical_percentage = len(df.select_dtypes(include=[np.number]).columns) / num_variables * 100
                        categorical_percentage = len(df.select_dtypes(include=['object']).columns) / num_variables * 100
            
                        # Additional metrics
                        max_observations = df.count().max()
                        min_observations = df.count().min()
            
                        # Layout
                        row1_col1, row1_col2 = st.columns(2)
                        row2_col1, row2_col2 = st.columns(2)
                        row3_col1, row3_col2 = st.columns(2)
                        row4_col1, row4_col2 = st.columns(2)
                        row5_col1, row5_col2 = st.columns(2)
            
                        # Display metrics
                        with row1_col1:
                            st.metric(label="Number of Variables", value=num_variables)
                        with row1_col2:
                            st.metric(label="Number of Observations", value=num_observations)
            
                        missing_delta_color = "off" if missing_cells == 0 else "inverse" if (missing_cells / (num_variables * num_observations)) * 100 > 1 else "normal"
                        with row2_col1:
                            st.metric(label="Missing Cells", value=missing_cells, delta=f"{(missing_cells / (num_variables * num_observations)) * 100:.1f}%",     delta_color=missing_delta_color)
                        
                        duplicate_delta_color = "off" if duplicate_rows == 0 else "inverse" if (duplicate_rows / num_observations) * 100 > 1 else "normal"
                        with row2_col2:
                            st.metric(label="Duplicate Rows", value=duplicate_rows, delta=f"{(duplicate_rows / num_observations) * 100:.1f}%", delta_color=duplicate_delta_color)
            
                        with row3_col1:
                            st.metric(label="Numerical Variables (%)", value=f"{numerical_percentage:.1f}%")
                        with row3_col2:
                            st.metric(label="Categorical Variables (%)", value=f"{categorical_percentage:.1f}%")
            
                        with row4_col1:
                            st.metric(label="Max Observations per Feature", value=max_observations)
                        with row4_col2:
                            st.metric(label="Min Observations per Feature", value=min_observations)
            
                        with row5_col1:
                            st.metric(label="Total Size in Memory", value=f"{total_size / (1024 ** 2):.1f} MB")
                        with row5_col2:
                            st.metric(label="Average Record Size in Memory", value=f"{avg_record_size:.1f} B")
        
                # Tab 2: Variable Types
                with overview_tab2:
                    with st.spinner("loading ..."):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Numerical", len(df.select_dtypes(include=[np.number]).columns))
                            st.metric("Categorical", len(df.select_dtypes(include=['object']).columns))
                            st.metric("Boolean", df.select_dtypes(include=['bool']).shape[1])
                        with col2:
                            st.metric("Date", df.select_dtypes(include=['datetime']).shape[1])
                            st.metric("Text (Unique)", df.select_dtypes(include=['category']).shape[1])
        
                # Tab 3: Variables
                with overview_tab3:
                    with st.spinner("loading ..."):
                        st.write(df.columns.tolist())
                
                # Tab 4: Numerical Features
                with overview_tab4:
                    numerical_features = df.select_dtypes(include=[np.number]).columns.tolist()
                    categorical_features = df.select_dtypes(include=['object']).columns.tolist()

                    with st.spinner("loading ..."):
                        col1, col2 = st.columns(2)
                        with col1:
                            if numerical_features:  # Check if there are numerical features
                                st.write("##### Numerical Features")
                                st.write(numerical_features)
                            else:
                                st.write("No numerical features found in the dataset.")
                        
                        with col2:
                            if categorical_features:  # Check if there are categorical features
                                st.write("##### Categorical Features")
                                st.write(categorical_features)
                            else:
                                st.write("No categorical features found in the dataset.")
                
        
                # Tab 4: Warnings
                with overview_tab5:
                    with st.spinner("loading ..."):
                        if warnings:
                            for warning in warnings:
                                col_name, message, warning_type = warning
                                if warning_type == "missing":
                                    st.write(f"<span style='color: red;'>{col_name}</span> {message} <span style='background-color: #f0ad4e; color: white; padding: 2px 6px;     border-radius: 4px;        '>Missing</span>", unsafe_allow_html=True)
                                elif warning_type == "warning":
                                    st.write(f"<span style='color: red;'>{col_name}</span> {message} <span style='background-color: rgb(255,0,0,0.7); color: white; padding: 2px     6px;         border-radius: 4px;'>Warning</span>", unsafe_allow_html=True)
                                elif warning_type == "skewed":
                                    st.write(f"<span style='color: red;'>{col_name}</span> {message} <span style='background-color: #5bc0de; color: white; padding: 2px 6px;     border-radius: 4px;        '>Skewed</span>", unsafe_allow_html=True)
                        else:
                            st.write("No warnings")
        
                # Tab 5: Numerical Features

        
        
        with dataqualityinsights:
            with st.container(border=True, height=610):  # Adjust height for additional tabs
                st.write("### Data Quality Insights")
        
                dataqualityinsights_tab1, dataqualityinsights_tab2, dataqualityinsights_tab3, dataqualityinsights_tab4, dataqualityinsights_tab5, dataqualityinsights_tab6, dataqualityinsights_tab7, dataqualityinsights_tab8, dataqualityinsights_tab9 = st.tabs([
                    "Missing Values",
                    "Duplicates",
                    "Unique Value",
                    "High Cardinality",
                    "Most Frequent Values",
                    "Distribution",
                    "Statistics",
                    "Data Type",
                    "Memory Usage"
                ])
        
                # Tab 1: Missing Values
                with dataqualityinsights_tab1:

                    missing_values = df.isnull().sum().reset_index()
                    missing_values.columns = ['Feature', 'Missing Values']
                    missing_values['Percentage'] = (missing_values['Missing Values'] / df.shape[0]) * 100
        
                    if missing_values['Missing Values'].sum() > 0:
                        col1, col2 = st.columns([0.40, 0.60])
                        with col1:
                            with st.spinner("loading Missing Values per Feature ..."):
                                st.write(missing_values)
                        with col2:
                            with st.spinner("loading Missing Values per Feature Chart ..."):
                                fig = px.bar(
                                    missing_values,
                                    x='Feature',
                                    y='Missing Values',
                                    title='Missing Values per Feature',
                                    text_auto='.2s',
                                    color_discrete_sequence=["#9933FF"]
                                )
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.success("No missing values found in the dataset.")
        
                # Tab 2: Duplicates
                with dataqualityinsights_tab2:
                    duplicate_rows = df[df.duplicated()]
                    duplicate_count = duplicate_rows.shape[0]
        
                    if duplicate_count > 0:
                        col1, col2 = st.columns([0.40, 0.60])
                        with col1:
                            with st.spinner("loading Duplicate Rows ..."):
                                st.write(duplicate_rows.head())
                        with col2:
                            with st.spinner("loading Duplicate Rows Chart ..."):
                                fig = px.bar(
                                    x=["Duplicates", "Unique"],
                                    y=[duplicate_count, df.shape[0] - duplicate_count],
                                    title='Duplicate vs Unique Rows',
                                    text_auto='.2s',
                                    labels={'x': 'Row Type', 'y': 'Count'},
                                    color_discrete_sequence=["#9933FF"]
                                )
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.success("No duplicate rows found in the dataset.")
        
                # Tab 3: Unique Value
                with dataqualityinsights_tab3:
                    unique_values = df.nunique().reset_index()
                    unique_values.columns = ['Feature', 'Unique Values']
        
                    col1, col2 = st.columns([0.40, 0.60])
                    with col1:
                        with st.spinner("loading Unique Values per Feature ..."):
                            st.write(unique_values)
                    with col2:
                        with st.spinner("loading Unique Values per Feature Chart ..."):
                            fig = px.bar(
                                unique_values,
                                x='Feature',
                                y='Unique Values',
                                title='Unique Values per Feature',
                                text_auto='.2s',
                                color_discrete_sequence=["#9933FF"]
                            )
                            st.plotly_chart(fig, use_container_width=True)
        
                # Tab 4: High Cardinality
                with dataqualityinsights_tab4:
                    cardinality = df.nunique().reset_index()
                    cardinality.columns = ['Feature', 'Unique Values']
                    cardinality['Percentage'] = (cardinality['Unique Values'] / df.shape[0]) * 100
        
                    high_cardinality = cardinality[cardinality['Percentage'] > 50]
        
                    if not high_cardinality.empty:
                        col1, col2 = st.columns([0.40, 0.60])
                        with col1:
                            with st.spinner("loading High Cardinality Features ..."):
                                st.write(high_cardinality)
                        with col2:
                            with st.spinner("loading High Cardinality Features Chart ..."):                            
                                fig = px.bar(
                                    high_cardinality,
                                    x='Feature',
                                    y='Unique Values',
                                    title='High Cardinality Features',
                                    text_auto='.2s',
                                    color_discrete_sequence=["#9933FF"]
                                )
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.success("No features with high cardinality found.")

                with dataqualityinsights_tab5:
                    # User can select a feature to analyze
                    selected_feature = st.selectbox("Select a Feature to Analyze", df.columns)
                
                    # Calculate Most Frequent Values
                    most_frequent = df[selected_feature].value_counts().reset_index()
                    most_frequent.columns = [selected_feature, 'Count']
                
                    col1, col2 = st.columns([0.40, 0.60])
                
                    # Display Table of Most Frequent Values in the Left Column
                    with col1:
                        with st.spinner(f"loading Most Frequent Values for {selected_feature} ..."):  
                            st.write(f"###### Most Frequent Values for {selected_feature}")
                            st.dataframe(most_frequent)
                
                    # Display Pie Chart of Most Frequent Values in the Right Column
                    with col2:
                        with st.spinner(f"loading Most Frequent Values for {selected_feature} Pie Chart..."):  
                            fig = px.pie(
                                most_frequent,
                                names=selected_feature,
                                values='Count',
                                title=f"Distribution of Most Frequent Values for {selected_feature}",
                                hole=0.3
                            )
                    
                            # Add text and hover info
                            fig.update_traces(
                                textposition='inside',
                                textinfo='label+percent',
                                hoverinfo='label+value+percent'
                            )
                    
                            st.plotly_chart(fig, use_container_width=True)

                with dataqualityinsights_tab6:
                    # Check if there are numerical features
                    if numerical_features:
                        skewness_kurtosis = pd.DataFrame({
                            'Feature': numerical_features,
                            'Skewness': [df[feature].skew() for feature in numerical_features],
                            'Kurtosis': [df[feature].kurtosis() for feature in numerical_features]
                        })
                
                        # Create columns for layout
                        col1, col2 = st.columns([0.40, 0.60])
                
                        # Display the table in the first column
                        with col1:
                            with st.spinner("loading Skewness and Kurtosis of Numerical Features ..."):   
                                st.dataframe(skewness_kurtosis)
                
                        # Display the combined plot in the second column
                        with col2:
                            with st.spinner("loading Skewness and Kurtosis of Numerical Features Chart ..."):   
                                skewness_kurtosis_melted = skewness_kurtosis.melt(
                                    id_vars='Feature', 
                                    value_vars=['Skewness', 'Kurtosis'], 
                                    var_name='Metric', 
                                    value_name='Value'
                                )
                    
                                fig_combined = px.line(
                                    skewness_kurtosis_melted,
                                    x='Feature',
                                    y='Value',
                                    color='Metric',
                                    markers=True,
                                    title='Skewness and Kurtosis of Numerical Features'
                                )
                                fig_combined.update_layout(
                                    xaxis_title='Feature',
                                    yaxis_title='Value',
                                    legend_title='Metric'
                                )
                                st.plotly_chart(fig_combined, use_container_width=True)
                    else:
                        st.write("No numerical features found in the dataset.")

                with dataqualityinsights_tab7:
                    with st.spinner("loading Skewness and Kurtosis of Numerical Features Chart ..."):   
                        if not df[numerical_features].empty:
                            # Basic statistics
                            basic_stats = df[numerical_features].describe().transpose()
                    
                            # Advanced statistics
                            advanced_stats = pd.DataFrame({
                                'Feature': numerical_features,
                                'Coefficient of Variation': (df[numerical_features].std() / df[numerical_features].mean()).values,
                                'IQR': (df[numerical_features].quantile(0.75) - df[numerical_features].quantile(0.25)).values,
                                'Range': (df[numerical_features].max() - df[numerical_features].min()).values,
    
                            }).set_index('Feature')
                    
                            # Merge basic and advanced statistics
                            combined_stats = pd.concat([basic_stats, advanced_stats], axis=1)
                    
                            # Display combined statistics
                            st.dataframe(combined_stats)
                    
                        else:
                            st.write("No numerical columns found or DataFrame is empty.")

        
                with dataqualityinsights_tab8:
                    # Data Types Table
                    feature_data_types = df.dtypes.reset_index()
                    feature_data_types.columns = ['Feature', 'Data Type']
                
                    data_types_summary = df.dtypes.value_counts().reset_index()
                    data_types_summary.columns = ['Data Type', 'Count']
                
                    col1, col2 = st.columns([0.40, 0.60])
                
                    # Display Table of All Features and Their Data Types in the Left Column
                    with col1:
                        with st.spinner("loading Data Type Distribution ..."):  
                            st.dataframe(feature_data_types)  # Display all features and their data types
                
                    # Prepare Data for Pie Chart
                    data_types_summary['Data Type'] = data_types_summary['Data Type'].astype(str)  # Convert data types to strings for compatibility
                
                    # Pie Chart for Data Types in the Right Column
                    with col2:
                        with st.spinner("loading Data Type Distribution Chart ..."): 
                            fig = px.pie(
                                data_types_summary,
                                names='Data Type',
                                values='Count',
                                title='Data Type Distribution',
                                hole=0.3
                            )
                    
                            # Add data type names on the chart
                            fig.update_traces(
                                textposition='inside',  # Text inside the slices
                                textinfo='label+percent',  # Show label and percentage
                                hoverinfo='label+value+percent'  # Hover information
                            )
                    
                            st.plotly_chart(fig, use_container_width=True)


                # Tab 6: Memory Usage
                with dataqualityinsights_tab9:
                    memory_usage = df.memory_usage(deep=True).reset_index()
                    memory_usage.columns = ['Feature', 'Memory Usage (Bytes)']
        
                    col1, col2 = st.columns([0.40, 0.60])
                    with col1:
                        with st.spinner("loading Memory Usage per Feature ..."): 
                            st.write(memory_usage)
                    with col2:
                        with st.spinner("loading Memory Usage per Feature Chart ..."): 
                            fig = px.bar(
                                memory_usage,
                                x='Feature',
                                y='Memory Usage (Bytes)',
                                title='Memory Usage per Feature',
                                text_auto='.2s',
                                color_discrete_sequence=["#9933FF"]
                            )
                            st.plotly_chart(fig, use_container_width=True)
        

        # with st.container(border=True):
        #     st.subheader("Data Overview")

        #     tab1, tab2, tab3, tab4, tab5 = st.tabs([
        #         "Dataset Head", 
        #         "Dataset Middle", 
        #         "Dataset Footer", 
        #         "Full DataFrame", 
        #         "Interactive Exploration"
        #     ])
    
        #     with tab1:
        #         with st.spinner("loading Dataset Head ..."):
        #             st.write("##### Dataset Head")
        #             st.write(df.head())
    
        #     with tab2:
        #         with st.spinner("loading Dataset Middle ..."):
        #             st.write("##### Dataset Middle")
        #             st.write(df.iloc[len(df)//2:len(df)//2+5])
    
        #     with tab3:
        #         with st.spinner("loading Dataset Footer ..."):
        #             st.write("##### Dataset Footer")
        #             st.write(df.tail())
    
        #     with tab4:
        #         with st.spinner("loading Full DataFrame ..."):
        #             st.write("##### Full DataFrame")
        #             st.dataframe(df)
    
        #     with tab5:
        #         with st.spinner("loading Interactive Dataset Exploration ..."):
        #             st.write("##### Interactive Dataset Exploration")
        #             DatasetSummary.interactive_dataset_exploration(df)
                

    @staticmethod
    def interactive_dataset_exploration(df):
        """Allow users to explore the dataset interactively."""
        if df is not None:
            col1, col2, _, _ = st.columns([0.15, 0.15, 0.35, 0.35])

            with col1:
                column = st.selectbox("Select column to filter by", df.columns)
                unique_values = df[column].unique()

            with col2:
                filter_value = st.selectbox(f"Filter {column} by", unique_values)
                filtered_df = df[df[column] == filter_value]

            st.dataframe(filtered_df)
        else:
            st.error("No dataset loaded for exploration.")


def dataset_summary_page():
    load_css()

    st.header('Dataset Summary', divider='violet')

    if 'dataset_id' in st.session_state and 'dataset_name' in st.session_state:
        dataset_id = st.session_state['dataset_id']
        dataset_name = st.session_state['dataset_name']
        summary = DatasetSummary(dataset_id, dataset_name)

        # Corrected call to display_summary
        summary.display_summary()

        col1, col2 = st.columns([5.4, 1])
        with col1:
            if st.button("Back to Upload", key="back_to_upload"):
                st.session_state.uploaded = False
                st.switch_page("pages/dataset.py")
        with col2:
            if st.button("Go to Preprocessing", key="go_to_preprocessing"):
                st.session_state.df_to_preprocess = summary.dataset
                st.switch_page("pages/data_preprocessing.py")
    else:
        st.error("No dataset selected. Please go back and select a dataset.")

dataset_summary_page()
