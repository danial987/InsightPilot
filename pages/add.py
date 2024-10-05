import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

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

# Concrete strategy: Bar Chart
class BarChart(IVisualizationStrategy):
    def plot(self, df: pd.DataFrame, x_column: str, y_columns: list, z_column: str = None, show_legend: bool = True, show_labels: bool = True, chart_title: str = "", color_scheme: str = "Plotly", font_family: str = "Arial", font_size: int = 14, is_3d: bool = False) -> None:
        if x_column and y_columns:
            color_list = getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)

            fig = px.bar(df, x=x_column, y=y_columns, title=chart_title, color_discrete_sequence=color_list)

            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                legend=dict(font=dict(family=font_family, size=font_size)),
                showlegend=show_legend
            )

            if show_labels:
                fig.update_traces(texttemplate='%{y:.2s}', textposition='auto')

            st.plotly_chart(fig)
        else:
            st.warning("Please select both X and Y columns to generate a bar chart.")

# Concrete strategy: Line Chart (2D and 3D)
class LineChart(IVisualizationStrategy):
    def plot(self, df: pd.DataFrame, x_column: str, y_columns: list, z_column: str = None, show_legend: bool = True, show_labels: bool = True, chart_title: str = "", color_scheme: str = "Plotly", font_family: str = "Arial", font_size: int = 14, is_3d: bool = False) -> None:
        if x_column and y_columns:
            if is_3d and z_column:
                color_list = getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)

                fig = go.Figure()

                for y_col in y_columns:
                    fig.add_trace(go.Scatter3d(
                        x=df[x_column],
                        y=df[y_col],
                        z=df[z_column],
                        mode='lines+markers' if show_labels else 'lines',
                        marker=dict(size=5),
                        line=dict(width=2),
                        name=f'{y_col}'
                    ))

                fig.update_layout(
                    scene=dict(
                        xaxis_title=x_column,
                        yaxis_title='Y Axis',
                        zaxis_title=z_column
                    ),
                    title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                    legend=dict(font=dict(family=font_family, size=font_size)),
                    showlegend=show_legend
                )
            else:
                color_list = getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)

                fig = px.line(df, x=x_column, y=y_columns, title=chart_title, color_discrete_sequence=color_list)

                fig.update_layout(
                    title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                    legend=dict(font=dict(family=font_family, size=font_size)),
                    showlegend=show_legend
                )
                
                if show_labels:
                    fig.update_traces(mode='lines+markers')

            st.plotly_chart(fig)
        else:
            st.warning("Please select an X-axis column and at least one Y-axis column to generate a line chart.")

# Concrete strategy: Scatter Plot (2D and 3D)
class ScatterPlot(IVisualizationStrategy):
    def plot(self, df: pd.DataFrame, x_column: str, y_columns: list, z_column: str = None, show_legend: bool = True, show_labels: bool = True, chart_title: str = "", color_scheme: str = "Plotly", font_family: str = "Arial", font_size: int = 14, is_3d: bool = False) -> None:
        if x_column and y_columns:
            if is_3d and z_column:
                color_list = getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)

                fig = go.Figure()

                for y_col in y_columns:
                    fig.add_trace(go.Scatter3d(
                        x=df[x_column],
                        y=df[y_col],
                        z=df[z_column],
                        mode='markers',
                        marker=dict(size=5),
                        name=f'{y_col}'
                    ))

                fig.update_layout(
                    scene=dict(
                        xaxis_title=x_column,
                        yaxis_title='Y Axis',
                        zaxis_title=z_column
                    ),
                    title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                    legend=dict(font=dict(family=font_family, size=font_size)),
                    showlegend=show_legend
                )
            else:
                color_list = getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)

                fig = px.scatter(df, x=x_column, y=y_columns[0], title=chart_title, color_discrete_sequence=color_list)

                fig.update_layout(
                    title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                    legend=dict(font=dict(family=font_family, size=font_size)),
                    showlegend=show_legend
                )
                
                if show_labels:
                    fig.update_traces(marker=dict(size=12))

            st.plotly_chart(fig)
        else:
            st.warning("Please select an X-axis column and at least one Y-axis column to generate a scatter plot.")

# Concrete strategy: Box Plot
class BoxPlot(IVisualizationStrategy):
    def plot(self, df: pd.DataFrame, x_column: str, y_columns: list, z_column: str = None, show_legend: bool = True, show_labels: bool = True, chart_title: str = "", color_scheme: str = "Plotly", font_family: str = "Arial", font_size: int = 14, is_3d: bool = False) -> None:
        if x_column and y_columns:
            color_list = getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)

            fig = px.box(df, x=x_column, y=y_columns[0], points="all", title=chart_title, color_discrete_sequence=color_list)

            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                legend=dict(font=dict(family=font_family, size=font_size)),
                showlegend=show_legend
            )
            
            st.plotly_chart(fig)
        else:
            st.warning("Please select an X-axis column and at least one Y-axis column to generate a box plot.")

# Concrete strategy: Histogram
class Histogram(IVisualizationStrategy):
    def plot(self, df: pd.DataFrame, x_column: str, y_columns: list = None, z_column: str = None, show_legend: bool = True, show_labels: bool = True, chart_title: str = "", color_scheme: str = "Plotly", font_family: str = "Arial", font_size: int = 14, is_3d: bool = False) -> None:
        if x_column and y_columns:
            color_list = getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)

            fig = px.histogram(df, x=x_column, y=y_columns[0], title=chart_title, color_discrete_sequence=color_list)

            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                legend=dict(font=dict(family=font_family, size=font_size)),
                showlegend=show_legend
            )
            
            st.plotly_chart(fig)
        else:
            st.warning("Please select an X-axis column and one Y-axis column to generate a histogram.")

# Concrete strategy: Correlation Matrix with Plotly (including 3D support)
class CorrelationMatrix(IVisualizationStrategy):
    def plot(self, df: pd.DataFrame, x_column: str = None, y_columns: list = None, z_column: str = None, show_legend: bool = True, show_labels: bool = True, chart_title: str = "", color_scheme: str = "Viridis", font_family: str = "Arial", font_size: int = 14, is_3d: bool = False) -> None:
        # Map color scheme to valid Plotly colorscales
        colorscale_map = {
            "Plotly": "plotly3",
            "D3": "d3",
            "G10": "rainbow",
            "T10": "turbo",
            "Alphabet": "speed",
            "Dark24": "darkmint",
            "Set3": "matter",
            "Viridis": "viridis"  # Default value
        }

        # Filter numeric columns
        numeric_df = df[y_columns] if y_columns else df.select_dtypes(include=['number'])

        # Ensure there are enough numeric columns for correlation matrix
        if numeric_df.shape[1] < 2:
            st.warning("Not enough numeric columns for correlation matrix.")
            return

        # Calculate the correlation matrix
        correlation_matrix = numeric_df.corr()

        # Get the valid colorscale for 3D or 2D from the map
        colorscale = colorscale_map.get(color_scheme, "Viridis")

        if is_3d:
            # Create a 3D surface plot for the correlation matrix
            fig = go.Figure(data=[go.Surface(z=correlation_matrix.values, colorscale=colorscale)])

            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                scene=dict(
                    xaxis=dict(title="Features", tickvals=list(range(len(correlation_matrix.columns))),
                               ticktext=correlation_matrix.columns),
                    yaxis=dict(title="Features", tickvals=list(range(len(correlation_matrix.index))),
                               ticktext=correlation_matrix.index),
                    zaxis=dict(title="Correlation", range=[-1, 1]),
                ),
                margin=dict(l=65, r=50, b=65, t=90)
            )
        else:
            # Create a heatmap of the correlation matrix for 2D
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale=colorscale,
                text=correlation_matrix.values,  # Show correlation values
                hoverinfo="text"  # Show values when hovered
            ))

            if show_labels:
                fig.update_traces(texttemplate="%{text:.2f}", textfont=dict(size=font_size))

            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                xaxis=dict(tickfont=dict(family=font_family, size=font_size)),
                yaxis=dict(tickfont=dict(family=font_family, size=font_size)),
                coloraxis_colorbar=dict(title="Correlation"),
                showlegend=show_legend
            )

        # Render the correlation matrix using Streamlit
        st.plotly_chart(fig)


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
            chart_type = st.selectbox("Select Chart Type", ["Pie Chart", "Bar Chart", "Line Chart", "Scatter Plot", "Box Plot", "Histogram", "Correlation Matrix"], help="Choose a chart type.")

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

            elif chart_type == "Bar Chart":
                context = VisualizationContext(BarChart())

                numerical_columns = df.select_dtypes(include=['number']).columns.tolist()

                if len(numerical_columns) == 0:
                    st.warning(f"No numerical columns found in the dataset for {chart_type}.")
                    return

                x_column = st.selectbox("Select X-axis", numerical_columns)
                y_columns = st.multiselect("Select Y-axis", numerical_columns)

                col3, col4 = st.columns(2)
                with col3:
                    show_legend = st.checkbox("Show Legend", value=True)
                with col4:
                    show_labels = st.checkbox("Show Labels", value=True)

                chart_title = st.text_input("Chart Title", value=f"{chart_type}")

                color_schemes = ['Plotly', 'D3', 'G10', 'T10', 'Alphabet', 'Dark24', 'Set3']
                color_scheme = st.selectbox("Select Color Scheme", color_schemes)
                font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                font_size = st.slider("Font Size", 10, 30, value=14)

                st.session_state.x_column = x_column
                st.session_state.y_columns = y_columns
                st.session_state.show_legend = show_legend
                st.session_state.show_labels = show_labels
                st.session_state.chart_title = chart_title
                st.session_state.color_scheme = color_scheme
                st.session_state.font_family = font_family
                st.session_state.font_size = font_size

            elif chart_type in ["Line Chart", "Scatter Plot", "Box Plot", "Histogram"]:
                context = VisualizationContext(LineChart() if chart_type == "Line Chart" else ScatterPlot() if chart_type == "Scatter Plot" else BoxPlot() if chart_type == "Box Plot" else Histogram())

                numerical_columns = df.select_dtypes(include=['number']).columns.tolist()

                if len(numerical_columns) == 0:
                    st.warning(f"No numerical columns found in the dataset for {chart_type}.")
                    return

                x_column = st.selectbox("Select X-axis", numerical_columns)
                y_columns = st.multiselect("Select Y-axis", numerical_columns) if chart_type != "Histogram" else [st.selectbox("Select Y-axis", numerical_columns)]

                is_3d = st.checkbox("Enable 3D Chart") if chart_type in ["Line Chart", "Scatter Plot"] else False
                z_column = st.selectbox("Select Z-axis for 3D Chart", numerical_columns) if is_3d else None

                col3, col4 = st.columns(2)
                with col3:
                    show_legend = st.checkbox("Show Legend", value=True)
                with col4:
                    show_labels = st.checkbox("Show Markers" if chart_type != "Box Plot" else "Show Labels", value=True)

                chart_title = st.text_input("Chart Title", value=f"{chart_type}")

                color_schemes = ['Plotly', 'D3', 'G10', 'T10', 'Alphabet', 'Dark24', 'Set3']
                color_scheme = st.selectbox("Select Color Scheme", color_schemes)
                font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                font_size = st.slider("Font Size", 10, 30, value=14)

                st.session_state.x_column = x_column
                st.session_state.y_columns = y_columns
                st.session_state.z_column = z_column
                st.session_state.is_3d = is_3d
                st.session_state.show_legend = show_legend
                st.session_state.show_labels = show_labels
                st.session_state.chart_title = chart_title
                st.session_state.color_scheme = color_scheme
                st.session_state.font_family = font_family
                st.session_state.font_size = font_size

            elif chart_type == "Correlation Matrix":
                context = VisualizationContext(CorrelationMatrix())

                numerical_columns = df.select_dtypes(include=['number']).columns.tolist()

                if len(numerical_columns) == 0:
                    st.warning("No numerical columns found in the dataset for correlation matrix.")
                    return

                selected_columns = st.multiselect("Select features for Correlation Matrix", numerical_columns, default=numerical_columns)

                # Show 3D chart toggle directly after selecting features
                if selected_columns:
                    is_3d = st.checkbox("Enable 3D Chart", value=False)

                chart_title = st.text_input("Chart Title", value="Correlation Matrix")

                font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                font_size = st.slider("Font Size", 10, 30, value=14)

                st.session_state.selected_columns = selected_columns
                st.session_state.chart_title = chart_title
                st.session_state.font_family = font_family
                st.session_state.font_size = font_size
                st.session_state.is_3d = is_3d if selected_columns else False

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
                elif chart_type in ["Bar Chart", "Line Chart", "Scatter Plot", "Box Plot", "Histogram"] and st.session_state.x_column and st.session_state.y_columns:
                    st.write("### Chart Preview")
                    context.create_visualization(
                        df,
                        st.session_state.x_column,
                        st.session_state.y_columns,
                        st.session_state.z_column,
                        st.session_state.show_legend,
                        st.session_state.show_labels,
                        st.session_state.chart_title,
                        st.session_state.color_scheme,
                        st.session_state.font_family,
                        st.session_state.font_size,
                        st.session_state.is_3d
                    )
                elif chart_type == "Correlation Matrix" and st.session_state.selected_columns:
                    st.write("### Chart Preview")
                    context.create_visualization(
                        df,
                        None,
                        st.session_state.selected_columns, 
                        None,
                        show_legend=True,
                        show_labels=True,
                        chart_title=st.session_state.chart_title,
                        font_family=st.session_state.font_family,
                        font_size=st.session_state.font_size,
                        is_3d=st.session_state.is_3d
                    )
                else:
                    st.warning(f"Please select appropriate features for {chart_type} to generate a chart.")

    else:
        st.warning("No dataset available for visualization. Please ensure you've completed the preprocessing step and saved the dataset.")

data_visualization_page()
