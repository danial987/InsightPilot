import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from statsmodels.graphics.mosaicplot import mosaic

# Interface for Visualization Strategy
class IVisualizationStrategy:
    def plot(self, df: pd.DataFrame, x_column: str = None, y_columns: list = None, z_column: str = None, show_legend: bool = True, show_labels: bool = True, chart_title: str = "", color_scheme: str = "Plotly", font_family: str = "Arial", font_size: int = 14, is_3d: bool = False) -> None:
        raise NotImplementedError("Visualization strategies must implement the plot method.")

# Concrete strategy: Pie Chart
class PieChart(IVisualizationStrategy):
    def plot(self, df: pd.DataFrame, x_column: str = None, y_columns: list = None, z_column: str = None, show_legend: bool = True, show_labels: bool = True, chart_title: str = "", color_scheme: str = "Plotly", font_family: str = "Arial", font_size: int = 14, is_3d: bool = False) -> None:
        if y_columns:
            combined_col_name = '_'.join(y_columns)
            df[combined_col_name] = df[y_columns].astype(str).agg('-'.join, axis=1)

            pie_chart_data = df[combined_col_name].value_counts().reset_index()
            pie_chart_data.columns = [combined_col_name, 'Count']

            color_list = getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)

            fig = px.pie(pie_chart_data, names=combined_col_name, values='Count', title=chart_title, color_discrete_sequence=color_list)

            fig.update_traces(textinfo='label+percent' if show_labels else 'percent', showlegend=show_legend)

            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                legend=dict(font=dict(family=font_family, size=font_size)),
                showlegend=show_legend
            )

            st.plotly_chart(fig)
        else:
            st.warning("Please select at least one feature to generate a pie chart.")

# Concrete strategy: Count Plot (New)
class CountPlot(IVisualizationStrategy):
    def plot(self, df: pd.DataFrame, x_column: str = None, y_columns: list = None, z_column: str = None, show_legend: bool = True, show_labels: bool = True, chart_title: str = "", color_scheme: str = "Plotly", font_family: str = "Arial", font_size: int = 14, is_3d: bool = False) -> None:
        if x_column:
            count_data = df[x_column].value_counts().reset_index()
            count_data.columns = [x_column, 'Count']

            color_list = getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)

            fig = px.bar(count_data, x=x_column, y='Count', title=chart_title, color_discrete_sequence=color_list)

            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                showlegend=False
            )

            if show_labels:
                fig.update_traces(texttemplate='%{y}', textposition='auto')

            st.plotly_chart(fig)
        else:
            st.warning("Please select a valid column for the Count Plot.")

# Other strategies (BarChart, LineChart, etc.) remain unchanged...
# Context class for Visualization
class VisualizationContext:
    def __init__(self, strategy: IVisualizationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: IVisualizationStrategy):
        self._strategy = strategy

    def create_visualization(self, df: pd.DataFrame, x_column: str = None, y_columns: list = None, z_column: str = None, show_legend: bool = True, show_labels: bool = True, chart_title: str = "", color_scheme: str = "Plotly", font_family: str = "Arial", font_size: int = 14, is_3d: bool = False):
        self._strategy.plot(df, x_column, y_columns, z_column, show_legend, show_labels, chart_title, color_scheme, font_family, font_size, is_3d)

# Main page for data visualization
def load_css():
    with open('static/style.css') as f:
        css_code = f.read()
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

def data_visualization_page():
    load_css()
    st.header('Data Visualization', divider='violet')

    # Initialize session state variables if they don't exist
    if 'x_column' not in st.session_state:
        st.session_state.x_column = None
    if 'y_columns' not in st.session_state:
        st.session_state.y_columns = []
    if 'z_column' not in st.session_state:
        st.session_state.z_column = None
    if 'is_3d' not in st.session_state:
        st.session_state.is_3d = False
    if 'selected_columns' not in st.session_state:
        st.session_state.selected_columns = []
    if 'show_legend' not in st.session_state:
        st.session_state.show_legend = True
    if 'show_labels' not in st.session_state:
        st.session_state.show_labels = True
    if 'chart_title' not in st.session_state:
        st.session_state.chart_title = ""
    if 'color_scheme' not in st.session_state:
        st.session_state.color_scheme = "Plotly"
    if 'font_family' not in st.session_state:
        st.session_state.font_family = "Arial"
    if 'font_size' not in st.session_state:
        st.session_state.font_size = 14

    if 'df_to_visualize' in st.session_state:
        data = st.session_state.df_to_visualize

        if isinstance(data, bytes):
            df = pd.read_csv(io.StringIO(data.decode('utf-8')))
        else:
            df = data

        dataset_name = st.session_state.dataset_name_to_visualize
        with st.container(border=True):
            st.write(f"Visualizing Dataset: {dataset_name}")

        with st.container(border=True):
            col1, col2 = st.columns([1, 2.5])

        with col1:
            chart_type = st.selectbox("Select Chart Type", ["Pie Chart", "Bar Chart", "Line Chart", "Scatter Plot", "Box Plot", "Histogram", "Correlation Matrix", "HeatMap", "Mosaic Plot", "Count Plot"], help="Choose a chart type.")

            if chart_type == "Pie Chart":
                context = VisualizationContext(PieChart())

                categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

                if len(categorical_columns) == 0:
                    st.warning("No categorical columns found in the dataset for pie chart.")
                    return

                selected_columns = st.multiselect("Select categorical features for Pie Chart", categorical_columns)

                col3, col4 = st.columns(2)
                with col3:
                    show_legend = st.checkbox("Show Legend", value=True)
                with col4:
                    show_labels = st.checkbox("Show Labels", value=True)

                chart_title = st.text_input("Chart Title", value="Pie Chart")

                color_schemes = ['Plotly', 'D3', 'G10', 'T10', 'Alphabet', 'Dark24', 'Set3']
                color_scheme = st.selectbox("Select Color Scheme", color_schemes)
                font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                font_size = st.slider("Font Size", 10, 30, value=14)

                st.session_state.selected_columns = selected_columns
                st.session_state.show_legend = show_legend
                st.session_state.show_labels = show_labels
                st.session_state.chart_title = chart_title
                st.session_state.color_scheme = color_scheme
                st.session_state.font_family = font_family
                st.session_state.font_size = font_size

            elif chart_type == "Count Plot":
                context = VisualizationContext(CountPlot())
                categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

                if len(categorical_columns) == 0:
                    st.warning("No categorical columns found in the dataset for count plot.")
                    return

                x_column = st.selectbox("Select X-axis", categorical_columns)

                chart_title = st.text_input("Chart Title", value="Count Plot")

                color_schemes = ['Plotly', 'D3', 'G10', 'T10', 'Alphabet', 'Dark24', 'Set3']
                color_scheme = st.selectbox("Select Color Scheme", color_schemes)
                font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                font_size = st.slider("Font Size", 10, 30, value=14)

                st.session_state.x_column = x_column
                st.session_state.chart_title = chart_title
                st.session_state.color_scheme = color_scheme
                st.session_state.font_family = font_family
                st.session_state.font_size = font_size

        with col2:
            with st.spinner("Generating Chart..."):
                if chart_type == "Pie Chart" and st.session_state.selected_columns:
                    st.write("### Chart Preview")
                    context.create_visualization(
                        df, 
                        None, 
                        st.session_state.selected_columns, 
                        None,
                        st.session_state.show_legend,
                        st.session_state.show_labels,
                        st.session_state.chart_title,
                        st.session_state.color_scheme,
                        st.session_state.font_family,
                        st.session_state.font_size
                    )
                elif chart_type == "Count Plot" and st.session_state.x_column:
                    st.write("### Chart Preview")
                    context.create_visualization(
                        df,
                        st.session_state.x_column,
                        None,
                        None,
                        show_legend=False,
                        show_labels=True,
                        chart_title=st.session_state.chart_title,
                        color_scheme=st.session_state.color_scheme,
                        font_family=st.session_state.font_family,
                        font_size=st.session_state.font_size
                    )
                # Other chart types remain unchanged...

    else:
        st.warning("No dataset available for visualization. Please ensure you've completed the preprocessing step and saved the dataset.")

data_visualization_page()
