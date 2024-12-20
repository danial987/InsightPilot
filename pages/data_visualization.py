import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from statsmodels.graphics.mosaicplot import mosaic
import numpy as np
import json  # Add this import at the top of your file
from abc import ABC, abstractmethod
import os

class IVisualizationStrategy(ABC):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str = None, 
             y_columns: list = None, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Plotly", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:

        raise NotImplementedError("Visualization strategies must implement the plot method.")
        

class CountPlot(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str = None, 
             y_columns: list = None, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Plotly", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:

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
            

class PieChart(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str = None, 
             y_columns: list = None, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Plotly", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:

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
            fig = go.Figure()
            fig.add_annotation(
                text="No features selected for Pie Chart.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(family=font_family, size=font_size, color="red")
            )
            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            st.plotly_chart(fig)


class BarChart(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str, 
             y_columns: list, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Viridis", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:
        
        if not x_column or not y_columns:
            st.warning("Please select an X-axis column and at least one Y-axis column to generate a bar chart.")
            return

        missing_columns = [
            col for col in ([x_column] + y_columns + ([z_column] if z_column else []))
            if col and col not in df.columns
        ]
        if missing_columns:
            st.warning(f"The following columns are missing in the DataFrame: {', '.join(missing_columns)}")
            return

        if is_3d and z_column:
            if len(df[x_column]) != len(df[z_column]) or len(df[y_columns[0]]) != len(df[z_column]):
                st.warning(f"The Z column `{z_column}` is invalid or does not match the length of the X and Y columns.")
                return

        if is_3d and z_column:
            fig = go.Figure()

            x = df[x_column]
            y = df[y_columns[0]]
            z = df[z_column]

            fig.add_trace(go.Mesh3d(
                x=np.repeat(x, 4), 
                y=np.repeat(y, 4), 
                z=[item for i in range(len(z)) for item in [0, 0, z.iloc[i], z.iloc[i]]],
                intensity=z,  
                colorscale='Viridis', 
                opacity=0.5
            ))

            fig.update_layout(
                scene=dict(
                    xaxis_title=x_column,
                    yaxis_title=y_columns[0],
                    zaxis_title=z_column
                ),
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                showlegend=show_legend
            )

        else:
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


class LineChart(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str, 
             y_columns: list, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Plotly", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:
             
        if is_3d and z_column is None:
            st.warning("Please select a valid Z-axis column to generate a 3D line chart.")
            return
        
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


class ScatterPlot(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str, 
             y_columns: list, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Plotly", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:

        if x_column and y_columns:
            if is_3d:
                if not z_column:
                    st.warning("Please select valid X, Y, and Z columns for the 3D scatter plot.")
                    return

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


class BoxPlot(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str, 
             y_columns: list, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Plotly", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:

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

                     

class Histogram(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str, 
             y_columns: list = None, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Plotly", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:

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


class CorrelationMatrix(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str = None, 
             y_columns: list = None, 
             z_column: str = None,
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "",
             color_scheme: str = "Viridis", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:
        
        colorscale_map = {
            "Plotly": "plotly3",
            "D3": "d3",
            "G10": "rainbow",
            "T10": "turbo",
            "Alphabet": "speed",
            "Dark24": "darkmint",
            "Set3": "matter",
            "Viridis": "viridis"
        }

        if y_columns:
            invalid_columns = [col for col in y_columns if col not in df.columns]
            if invalid_columns:
                st.warning(f"Invalid columns: {', '.join(invalid_columns)}. Please provide valid numeric columns.")
                return

        numeric_df = df[y_columns] if y_columns else df.select_dtypes(include=['number'])

        if numeric_df.shape[1] < 2:
            st.warning("Not enough numeric columns for correlation matrix.")
            return

        correlation_matrix = numeric_df.corr()
        colorscale = colorscale_map.get(color_scheme, "Viridis")

        if is_3d:
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
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale=colorscale,
                text=correlation_matrix.values,
                hoverinfo="text"
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

        st.plotly_chart(fig)


class HeatMap(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str = None, 
             y_columns: list = None, 
             z_column: str = None, 
             show_legend: bool = True,
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Viridis", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:

        if y_columns is None or len(y_columns) < 2:
            st.warning("Please select at least two numeric columns to generate a heatmap.")
            return

        try:
            numeric_df = df[y_columns].select_dtypes(include=['number'])
        except KeyError as e:
            st.warning(f"Some columns specified were not found in the DataFrame: {e}")
            return

        correlation_matrix = numeric_df.corr()

        colorscale_map = {
            'Plotly': 'plotly3',
            'D3': 'd3',
            'G10': 'rainbow',
            'T10': 'turbo',
            'Alphabet': 'speed',
            'Dark24': 'darkmint',
            'Set3': 'matter',
            'Viridis': 'viridis',
            'Turbo': 'turbo'
        }

        valid_colorscale = colorscale_map.get(color_scheme, 'viridis')

        if is_3d:
            fig = go.Figure(data=[go.Surface(z=correlation_matrix.values, colorscale=valid_colorscale)])
            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                scene=dict(
                    xaxis=dict(tickvals=list(range(len(correlation_matrix.columns))),
                               ticktext=correlation_matrix.columns, title="Features"),
                    yaxis=dict(tickvals=list(range(len(correlation_matrix.index))),
                               ticktext=correlation_matrix.index, title="Features"),
                    zaxis=dict(title="Correlation"),
                )
            )
        else:
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale=valid_colorscale
            ))

            if show_labels:
                fig.update_traces(texttemplate="%{z:.2f}")

            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                xaxis=dict(tickfont=dict(family=font_family, size=font_size)),
                yaxis=dict(tickfont=dict(family=font_family, size=font_size))
            )

        st.plotly_chart(fig)


class MosaicPlot(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str = None, 
             y_columns: list = None, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Plotly", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:

        if not x_column or not y_columns:
            st.warning("Please select valid X and Y columns for the Mosaic plot.")
            return

        if x_column not in df.columns or y_columns[0] not in df.columns:
            st.warning("The specified columns are not present in the DataFrame. Please check your column names.")
            return

        top_n = 10
        try:
            df_filtered = df[df[x_column].isin(df[x_column].value_counts().index[:top_n])]
            df_filtered = df_filtered[df_filtered[y_columns[0]].isin(df_filtered[y_columns[0]].value_counts().index[:top_n])]

            df_grouped = df_filtered.groupby([x_column, y_columns[0]]).size().reset_index(name='Count')

        except ValueError as e:
            st.error(f"Error: {str(e)}. Please ensure the columns used for grouping don't conflict with existing column names.")
            return

        df_grouped['Proportion'] = df_grouped.groupby(x_column)['Count'].transform(lambda x: x / x.sum())

        fig = px.bar(
            df_grouped,
            x=x_column,
            y='Proportion',
            color=y_columns[0],
            text='Count',
            title=chart_title,
            labels={'Proportion': 'Proportion'},
            color_discrete_sequence=getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)
        )

        fig.update_layout(
            title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
            legend=dict(font=dict(family=font_family, size=font_size)),
            showlegend=show_legend
        )

        if show_labels:
            fig.update_traces(texttemplate='%{text:.2s}', textposition='auto')

        st.plotly_chart(fig)


class TreeMap(IVisualizationStrategy):
    def plot(self,
             df: pd.DataFrame,
             x_column: str = None,
             y_columns: list = None,
             z_column: str = None,
             show_legend: bool = True,
             show_labels: bool = True,
             chart_title: str = "",
             color_scheme: str = "Plotly",
             font_family: str = "Arial",
             font_size: int = 14,
             top_n: int = 5,
             is_3d: bool = False) -> None:

        if any(df.columns.duplicated()):
            st.error("Error: The DataFrame contains non-unique column labels. Please remove or rename duplicate columns.")
            return

        if not x_column or not y_columns:
            st.warning("Please select valid X and Y columns for the Tree Map.")
            return

        missing_columns = [col for col in [x_column] + y_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"The following columns are missing in the DataFrame: {', '.join(missing_columns)}")
            return

        y_columns = [col for col in y_columns if col != x_column]
        if not y_columns:
            st.warning("Please select at least one Y-axis column that is different from the X-axis column.")
            return

        try:
            df_filtered = df[df[x_column].isin(df[x_column].value_counts().index[:top_n])]
            for y_col in y_columns:
                df_filtered = df_filtered[df_filtered[y_col].isin(df_filtered[y_col].value_counts().index[:top_n])]
        except KeyError as e:
            st.error(f"Error filtering the DataFrame: {str(e)}")
            return

        conflict_columns = set(["Count"]) & set(df_filtered.columns)
        if conflict_columns:
            st.error(f"Error: cannot insert {', '.join(conflict_columns)}, already exists. Please ensure columns for grouping don't conflict with existing column names.")
            return

        try:
            df_grouped = df_filtered.groupby([x_column] + y_columns).size().reset_index(name='Count')
        except ValueError as e:
            st.error(f"Error: {str(e)}. Please ensure columns for grouping don't conflict with existing column names.")
            return

        color_list = getattr(px.colors.qualitative, color_scheme, px.colors.qualitative.Plotly)
        try:
            fig = px.treemap(
                df_grouped,
                path=[px.Constant(chart_title), x_column] + y_columns,
                values='Count',
                title=chart_title,
                color=x_column,
                color_discrete_sequence=color_list
            )
        except Exception as e:
            st.error(f"Error generating the Tree Map: {str(e)}")
            return

        fig.update_layout(
            title=dict(
                text=chart_title,
                font=dict(family=font_family, size=font_size)
            ),
            font=dict(
                family=font_family,
                size=font_size
            ),
            legend=dict(
                font=dict(family=font_family, size=font_size)
            ),
            showlegend=show_legend
        )

        if show_labels:
            fig.update_traces(texttemplate="%{label}")

        st.plotly_chart(fig)


class DensityPlot(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str, 
             y_columns: list = None, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Viridis", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:
        
        missing_columns = [
            col for col in ([x_column] + (y_columns or []) + ([z_column] if z_column else []))
            if col and col not in df.columns
        ]
        if missing_columns:
            st.warning(f"The following columns are missing in the DataFrame: {', '.join(missing_columns)}")
            return

        if x_column and y_columns:
            if len(y_columns) > 1:
                st.warning("Density plots only support a single Y-axis feature. Please select one Y-axis feature.")
                return

            if is_3d and z_column:
                valid_3d_colorscales = [
                    'aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance', 'blackbody', 'bluered', 
                    'blues', 'blugrn', 'bluyl', 'brbg', 'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 
                    'cividis', 'curl', 'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric', 
                    'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys', 'haline', 'hot', 'hsv', 
                    'ice', 'icefire', 'inferno', 'jet', 'magenta', 'magma', 'matter', 'mint', 'mrybm', 
                    'mygbm', 'oranges', 'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl', 
                    'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn', 'puor', 'purd', 
                    'purp', 'purples', 'purpor', 'rainbow', 'rdbu', 'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 
                    'redor', 'reds', 'solar', 'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 
                    'tealgrn', 'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid', 'turbo', 
                    'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr', 'ylorrd'
                ]
                if color_scheme.lower() not in valid_3d_colorscales:
                    color_scheme = 'Viridis'

                fig = go.Figure(data=go.Isosurface(
                    x=df[x_column],
                    y=df[y_columns[0]],
                    z=df[z_column],
                    isomin=0.1, 
                    isomax=1.0,
                    surface_count=10,
                    colorscale=color_scheme,
                ))

                fig.update_layout(
                    title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                    scene=dict(
                        xaxis_title=x_column,
                        yaxis_title=y_columns[0],
                        zaxis_title=z_column
                    ),
                    showlegend=show_legend
                )

            else:
                fig = px.density_contour(df, x=x_column, y=y_columns[0], title=chart_title)

                fig.update_layout(
                    title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                    showlegend=show_legend
                )

                if show_labels:
                    fig.add_scatter(x=df[x_column], y=df[y_columns[0]], mode='markers', marker=dict(color='rgba(0,0,0,0.5)'))

            st.plotly_chart(fig)
        else:
            st.warning("Please select valid X, Y, and optionally Z columns for the density plot.")


class ConePlot(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str, 
             y_columns: list = None, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Plotly", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:
        
        missing_columns = [
            col for col in ([x_column] + (y_columns or []) + [z_column])
            if col and col not in df.columns
        ]
        if missing_columns:
            st.warning(f"The following columns are missing in the DataFrame: {', '.join(missing_columns)}")
            return

        if x_column and y_columns and z_column:
            fig = go.Figure(go.Cone(
                x=df[x_column],
                y=df[y_columns[0]],  
                z=df[z_column],
                u=df[x_column], 
                v=df[y_columns[0]],  
                w=df[z_column],  
                colorscale='Viridis',
                showscale=True
            ))

            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                scene=dict(
                    xaxis_title=x_column,
                    yaxis_title=y_columns[0],
                    zaxis_title=z_column
                ),
                showlegend=show_legend
            )

            st.plotly_chart(fig)
        else:
            st.warning("Please select X, Y, and Z columns for the 3D Cone Plot.")


class StreamlinePlot(IVisualizationStrategy):
    def plot(self, 
             df: pd.DataFrame, 
             x_column: str, 
             y_columns: list = None, 
             z_column: str = None, 
             show_legend: bool = True, 
             show_labels: bool = True, 
             chart_title: str = "", 
             color_scheme: str = "Viridis", 
             font_family: str = "Arial", 
             font_size: int = 14, 
             is_3d: bool = False) -> None:
        
        colorscale_map = {
            "Viridis": "Viridis",
            "Plasma": "Plasma",
            "Inferno": "Inferno",
            "Cividis": "Cividis",
            "Turbo": "Turbo",
            "Rainbow": "Rainbow",
            "Plotly": "Viridis"
        }

        missing_columns = [
            col for col in ([x_column] + (y_columns or []) + [z_column])
            if col and col not in df.columns
        ]
        if missing_columns:
            st.warning(f"The following columns are missing in the DataFrame: {', '.join(missing_columns)}")
            return

        if x_column and y_columns and z_column:
            valid_colorscale = colorscale_map.get(color_scheme, 'Viridis')

            fig = go.Figure()

            fig.add_trace(go.Scatter3d(
                x=df[x_column],
                y=df[y_columns[0]], 
                z=df[z_column],
                mode='lines',
                line=dict(width=3, color=df[z_column], colorscale=valid_colorscale),
            ))

            fig.update_layout(
                title=dict(text=chart_title, font=dict(family=font_family, size=font_size)),
                scene=dict(
                    xaxis_title=x_column,
                    yaxis_title=y_columns[0],
                    zaxis_title=z_column
                ),
                showlegend=show_legend
            )

            st.plotly_chart(fig)
        else:
            st.warning("Please select X, Y, and Z columns for the 3D Streamline Plot.")


class VisualizationContext:
    def __init__(self, strategy: IVisualizationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: IVisualizationStrategy):
        self._strategy = strategy

    def create_visualization(self, 
                             df: pd.DataFrame, 
                             x_column: str = None, 
                             y_columns: list = None, 
                             z_column: str = None, 
                             show_legend: bool = True, 
                             show_labels: bool = True, 
                             chart_title: str = "", 
                             color_scheme: str = "Plotly", 
                             font_family: str = "Arial", 
                             font_size: int = 14, 
                             is_3d: bool = False, top_n: int = None):
                             
        if top_n is not None:
            self._strategy.plot(df, x_column, y_columns, z_column, show_legend, show_labels, chart_title, color_scheme, font_family, font_size, top_n, is_3d)
        else:
            self._strategy.plot(df, x_column, y_columns, z_column, show_legend, show_labels, chart_title, color_scheme, font_family, font_size, is_3d)


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


def data_visualization_page():
    load_css()

    st.header('Data Visualization', divider='violet')
    with st.spinner("Loading Please Wait ..."):


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
                try:
                    # First, try reading as CSV
                    df = pd.read_csv(io.BytesIO(data), encoding='utf-8')  # Using io.BytesIO to handle byte data
                except pd.errors.ParserError:
                    try:
                        # If CSV reading fails, try reading as Excel (.xls or .xlsx)
                        df = pd.read_excel(io.BytesIO(data), engine='openpyxl')  # `openpyxl` can handle both .xls and .xlsx
                    except Exception as e:
                        try:
                            # If 'openpyxl' fails, try using 'xlrd' engine for .xls files
                            df = pd.read_excel(io.BytesIO(data), engine='xlrd')
                        except Exception as e:
                            st.error("Unsupported file format or corrupted file.")
                            df = None
            else:
                df = data
    
            dataset_name = st.session_state.dataset_name_to_visualize
            # with st.container(border=True):
            #     st.write(f"Visualizing Dataset: {dataset_name}")
            with st.expander(f"Dataset: {dataset_name}"):
                st.dataframe(df)
    
            with st.container(border=True):
                col1, _, col2 = st.columns([0.20, 0.02, 0.78])
    
            with col1:
                chart_type = st.selectbox("Select Chart Type", ["Pie Chart", "Bar Chart", "Line Chart", "Scatter Plot", 
                                                    "Box Plot", "Histogram", "Correlation Matrix", "HeatMap", 
                                                    "Mosaic Plot", "Count Plot", "Tree Map", "Density Plot", 
                                                    "3D Cone Plot", "Streamline Plot"], help="Choose a chart type.")
    
    
                if chart_type == "Count Plot":
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
    
    
                elif chart_type == "Pie Chart":
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
    
                    is_3d = st.checkbox("Enable 3D Bar Chart")
                    z_column = st.selectbox("Select Z-axis for 3D Chart", numerical_columns) if is_3d else None
                
                    chart_title = st.text_input("Chart Title", value=f"{chart_type}")
                
                    color_schemes = ['Plotly', 'D3', 'G10', 'T10', 'Alphabet', 'Dark24', 'Set3']
                    color_scheme = st.selectbox("Select Color Scheme", color_schemes)
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
    
                    st.session_state.x_column = x_column
                    st.session_state.y_columns = y_columns
                    st.session_state.z_column = z_column
                    st.session_state.is_3d = is_3d
                    st.session_state.chart_title = chart_title
                    st.session_state.color_scheme = color_scheme
                    st.session_state.font_family = font_family
                    st.session_state.font_size = font_size
    
    
                elif chart_type == "Histogram":
                    context = VisualizationContext(Histogram())
    
                    numerical_columns = df.select_dtypes(include=['number']).columns.tolist()
    
                    if len(numerical_columns) == 0:
                        st.warning(f"No numerical columns found in the dataset for {chart_type}.")
                        return
    
                    x_column = st.selectbox("Select X-axis", numerical_columns)
                    y_columns = [st.selectbox("Select Y-axis", numerical_columns)]
                
                    chart_title = st.text_input("Chart Title", value=f"{chart_type}")
                
                    color_schemes = ['Plotly', 'D3', 'G10', 'T10', 'Alphabet', 'Dark24', 'Set3']
                    color_scheme = st.selectbox("Select Color Scheme", color_schemes)
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
                
                    st.session_state.x_column = x_column
                    st.session_state.y_columns = y_columns
                    st.session_state.chart_title = chart_title
                    st.session_state.color_scheme = color_scheme
                    st.session_state.font_family = font_family
                    st.session_state.font_size = font_size
    
    
                elif chart_type == "Box Plot":
                    context = VisualizationContext(BoxPlot())
    
                    numerical_columns = df.select_dtypes(include=['number']).columns.tolist()
    
                    if len(numerical_columns) == 0:
                        st.warning(f"No numerical columns found in the dataset for {chart_type}.")
                        return
    
                    x_column = st.selectbox("Select X-axis", numerical_columns)
                    y_columns = st.multiselect("Select Y-axis", numerical_columns)
                
                    chart_title = st.text_input("Chart Title", value=f"{chart_type}")
                
                    color_schemes = ['Plotly', 'D3', 'G10', 'T10', 'Alphabet', 'Dark24', 'Set3']
                    color_scheme = st.selectbox("Select Color Scheme", color_schemes)
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
    
                    st.session_state.x_column = x_column
                    st.session_state.y_columns = y_columns
                    st.session_state.chart_title = chart_title
                    st.session_state.color_scheme = color_scheme
                    st.session_state.font_family = font_family
                    st.session_state.font_size = font_size
    
    
                elif chart_type == "Scatter Plot":
                    context = VisualizationContext(ScatterPlot())
    
                    numerical_columns = df.select_dtypes(include=['number']).columns.tolist()
    
                    if len(numerical_columns) == 0:
                        st.warning(f"No numerical columns found in the dataset for {chart_type}.")
                        return
    
                    x_column = st.selectbox("Select X-axis", numerical_columns)
                    y_columns = st.multiselect("Select Y-axis", numerical_columns)
    
                    is_3d = st.checkbox("Enable 3D Scatter Plot")
                    z_column = st.selectbox("Select Z-axis for 3D Chart", numerical_columns) if is_3d else None
                
                    chart_title = st.text_input("Chart Title", value=f"{chart_type}")
                
                    color_schemes = ['Plotly', 'D3', 'G10', 'T10', 'Alphabet', 'Dark24', 'Set3']
                    color_scheme = st.selectbox("Select Color Scheme", color_schemes)
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
    
                    st.session_state.x_column = x_column
                    st.session_state.y_columns = y_columns
                    st.session_state.z_column = z_column
                    st.session_state.is_3d = is_3d
                    st.session_state.chart_title = chart_title
                    st.session_state.color_scheme = color_scheme
                    st.session_state.font_family = font_family
                    st.session_state.font_size = font_size
    
    
                elif chart_type == "Line Chart":
                    context = VisualizationContext(LineChart())
    
                    numerical_columns = df.select_dtypes(include=['number']).columns.tolist()
    
                    if len(numerical_columns) == 0:
                        st.warning(f"No numerical columns found in the dataset for {chart_type}.")
                        return
    
                    x_column = st.selectbox("Select X-axis", numerical_columns)
                    y_columns = st.multiselect("Select Y-axis", numerical_columns)
    
                    is_3d = st.checkbox("Enable 3D Line Chart")
                    z_column = st.selectbox("Select Z-axis for 3D Chart", numerical_columns) if is_3d else None
                
                    chart_title = st.text_input("Chart Title", value=f"{chart_type}")
                
                    color_schemes = ['Plotly', 'D3', 'G10', 'T10', 'Alphabet', 'Dark24', 'Set3']
                    color_scheme = st.selectbox("Select Color Scheme", color_schemes)
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
    
                    st.session_state.x_column = x_column
                    st.session_state.y_columns = y_columns
                    st.session_state.z_column = z_column
                    st.session_state.is_3d = is_3d
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
    
    
                elif chart_type == "HeatMap":
                    context = VisualizationContext(HeatMap())
    
                    numerical_columns = df.select_dtypes(include=['number']).columns.tolist()
    
                    if len(numerical_columns) == 0:
                        st.warning("No numerical columns found in the dataset for heatmap.")
                        return
    
                    selected_columns = st.multiselect("Select features for HeatMap", numerical_columns)
                
                    if selected_columns:
                        is_3d = st.checkbox("Enable 3D HeatMap", value=False)
                
                    chart_title = st.text_input("Chart Title", value="HeatMap")
                
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
    
                    st.session_state.selected_columns = selected_columns
                    st.session_state.chart_title = chart_title
                    st.session_state.font_family = font_family
                    st.session_state.font_size = font_size
                    st.session_state.is_3d = is_3d if selected_columns else False
    
    
                elif chart_type == "Mosaic Plot":
                    context = VisualizationContext(MosaicPlot())
    
                    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
                    if len(categorical_columns) == 0:
                        st.warning("No categorical columns found in the dataset for Mosaic plot.")
                        return
    
                    x_column = st.selectbox("Select X-axis", categorical_columns)
                    y_columns = st.multiselect("Select Y-axis", [col for col in categorical_columns if col != x_column])
                
                    chart_title = st.text_input("Chart Title", value="Mosaic Plot")
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
    
                    st.session_state.x_column = x_column
                    st.session_state.y_columns = y_columns
                    st.session_state.chart_title = chart_title
                    st.session_state.font_family = font_family
                    st.session_state.font_size = font_size
    
    
                elif chart_type == "Tree Map":
                    context = VisualizationContext(TreeMap())
    
                    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
                    if len(categorical_columns) == 0:
                        st.warning(f"No categorical columns found in the dataset for {chart_type}.")
                        return
    
                    x_column = st.selectbox("Select X-axis", categorical_columns)
                    y_columns = st.multiselect("Select Y-axis", [col for col in categorical_columns if col != x_column])
                
                    if x_column:
                        max_unique_x = df[x_column].nunique()
                    else:
                        max_unique_x = 1
                
                    if y_columns:
                        max_unique_y = df[y_columns[0]].nunique()
                    else:
                        max_unique_y = 1
                
                    max_categories = min(max_unique_x, max_unique_y)
                
                    top_n = st.slider("Select the number of top categories to display", min_value=1, max_value=max_categories, value=5)
                
                    chart_title = st.text_input("Chart Title", value=f"{chart_type}")
                
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
    
                    st.session_state.x_column = x_column
                    st.session_state.y_columns = y_columns
                    st.session_state.chart_title = chart_title
                    st.session_state.font_family = font_family
                    st.session_state.font_size = font_size
                    st.session_state.top_n = top_n
    
    
                elif chart_type == "Density Plot":
                    context = VisualizationContext(DensityPlot())
    
                    numerical_columns = df.select_dtypes(include=['number']).columns.tolist()
    
                    if len(numerical_columns) == 0:
                        st.warning("No numerical columns found in the dataset for density plot.")
                        return
    
                    x_column = st.selectbox("Select X-axis", numerical_columns)
                    y_columns = [st.selectbox("Select Y-axis", numerical_columns)]  
                
                    is_3d = st.checkbox("Enable 3D Density Plot")
    
                    z_column = st.selectbox("Select Z-axis", numerical_columns) if is_3d else None
                
                    chart_title = st.text_input("Chart Title", value="Density Plot")
                
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
    
                    st.session_state.x_column = x_column
                    st.session_state.y_columns = y_columns  
                    st.session_state.z_column = z_column 
                    st.session_state.is_3d = is_3d 
                    st.session_state.chart_title = chart_title
                    st.session_state.font_family = font_family
                    st.session_state.font_size = font_size
    
    
                elif chart_type == "3D Cone Plot":
                    context = VisualizationContext(ConePlot())
                    
                    numerical_columns = df.select_dtypes(include=['number']).columns.tolist()
                
                    if len(numerical_columns) < 6:
                        st.warning("3D Cone Plot requires at least 6 numerical columns (X, Y, Z, U, V, W).")
                        return
                
                    x_column = st.selectbox("Select X-axis", numerical_columns)
                    y_column = st.selectbox("Select Y-axis", numerical_columns)
                    z_column = st.selectbox("Select Z-axis", numerical_columns)
    
                    u_column = st.selectbox("Select U (vector X)", numerical_columns)
                    v_column = st.selectbox("Select V (vector Y)", numerical_columns)
                    w_column = st.selectbox("Select W (vector Z)", numerical_columns)
                
                    chart_title = st.text_input("Chart Title", value="3D Cone Plot")
                
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
                
                    st.session_state.x_column = x_column
                    st.session_state.y_column = y_column
                    st.session_state.z_column = z_column
                    st.session_state.u_column = u_column
                    st.session_state.v_column = v_column
                    st.session_state.w_column = w_column
                    st.session_state.chart_title = chart_title
                    st.session_state.font_family = font_family
                    st.session_state.font_size = font_size
    
    
                elif chart_type == "Streamline Plot":
                    context = VisualizationContext(StreamlinePlot())
                
                    numerical_columns = df.select_dtypes(include=['number']).columns.tolist()
                
                    if len(numerical_columns) == 0:
                        st.warning("No numerical columns found in the dataset for Streamline plot.")
                        return
                
                    x_column = st.selectbox("Select X-axis", numerical_columns)
                    y_columns = [st.selectbox("Select Y-axis", numerical_columns)] 
                    z_column = st.selectbox("Select Z-axis", numerical_columns)
                
                    chart_title = st.text_input("Chart Title", value="Streamline Plot")
                
                    font_family = st.selectbox("Font Family", ["Arial", "Courier New", "Times New Roman", "Verdana"])
                    font_size = st.slider("Font Size", 10, 30, value=14)
                
                    st.session_state.x_column = x_column
                    st.session_state.y_columns = y_columns 
                    st.session_state.z_column = z_column
                    st.session_state.chart_title = chart_title
                    st.session_state.font_family = font_family
                    st.session_state.font_size = font_size
    
    
            with col2:
                with st.spinner("Generating Chart..."):
                    if chart_type == "Pie Chart":
                        if st.session_state.selected_columns:
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
                        else:
                            st.error("Please select at least one categorical feature to generate the Pie Chart.")
    
    
                    elif chart_type == "Histogram":
                        if st.session_state.x_column and st.session_state.y_columns:
                            st.write("### Chart Preview")
                            context.create_visualization(
                                df,
                                st.session_state.x_column,
                                st.session_state.y_columns,
                                None, 
                                st.session_state.show_legend,
                                st.session_state.show_labels,
                                st.session_state.chart_title,
                                st.session_state.color_scheme,
                                st.session_state.font_family,
                                st.session_state.font_size,
                                False  
                            )
                        else:
                            st.error("Please select both X-axis and Y-axis columns to generate the Histogram.")
    
    
                    elif chart_type == "Count Plot":
                        if st.session_state.x_column:
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
                        else:
                            st.error("Please select a column for the X-axis to generate the Count Plot.")
    
    
                    elif chart_type == "Scatter Plot":
                        if st.session_state.x_column and st.session_state.y_columns:
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
                        else:
                            st.error("Please select both X-axis and Y-axis columns to generate the Scatter Plot.")
    
    
                    elif chart_type == "Line Chart":
                        if st.session_state.x_column and st.session_state.y_columns:
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
                        else:
                            st.error("Please select both X-axis and Y-axis columns to generate the Line Chart.")
    
    
                    elif chart_type == "Bar Chart":
                        if st.session_state.x_column and st.session_state.y_columns:
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
                        else:
                            st.error("Please select both X-axis and Y-axis columns to generate the Bar Chart.")
    
    
                    elif chart_type == "Box Plot":
                        if st.session_state.x_column and st.session_state.y_columns:
                            st.write("### Chart Preview")
                            context.create_visualization(
                                df,
                                st.session_state.x_column,
                                st.session_state.y_columns,
                                None, 
                                st.session_state.show_legend,
                                st.session_state.show_labels,
                                st.session_state.chart_title,
                                st.session_state.color_scheme,
                                st.session_state.font_family,
                                st.session_state.font_size,
                                False 
                            )
                        else:
                            st.error("Please select both X-axis and Y-axis columns to generate the Box Plot.")
    
    
                    elif chart_type == "Correlation Matrix":
                        if st.session_state.selected_columns:
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
                            st.error("Please select at least two features to generate the Correlation Matrix.")
    
     
                    elif chart_type == "HeatMap":
                        if st.session_state.selected_columns and len(st.session_state.selected_columns) >= 2:
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
                            st.error("Please select at least two numeric columns to generate the HeatMap.")
    
    
                    elif chart_type == "Tree Map":
                        if st.session_state.x_column and st.session_state.y_columns:
                            st.write("### Chart Preview")
                            context.create_visualization(
                                df,
                                st.session_state.x_column,
                                st.session_state.y_columns, 
                                None,
                                show_legend=False,
                                show_labels=True,
                                chart_title=st.session_state.chart_title,
                                color_scheme=st.session_state.color_scheme,
                                font_family=st.session_state.font_family,
                                font_size=st.session_state.font_size,
                                top_n=st.session_state.top_n
                            )
                        else:
                            st.error("Please select both X and Y columns to generate the Tree Map.")
    
    
                    if chart_type == "Mosaic Plot":
                        if st.session_state.x_column and st.session_state.y_columns:
                            st.write("### Chart Preview")
                            context.create_visualization(
                                df,
                                st.session_state.x_column,
                                st.session_state.y_columns,
                                None,
                                show_legend=False,
                                show_labels=True,
                                chart_title=st.session_state.chart_title,
                                color_scheme=st.session_state.color_scheme,
                                font_family=st.session_state.font_family,
                                font_size=st.session_state.font_size
                            )
                        else:
                            st.error("Please select both X and Y columns to generate the Mosaic plot.")
    
    
                    if chart_type == "Density Plot":
                        if st.session_state.x_column and st.session_state.y_columns:
                            st.write("### Chart Preview")
                            context.create_visualization(
                                df,
                                st.session_state.x_column,
                                st.session_state.y_columns,
                                st.session_state.z_column,
                                show_legend=False,
                                show_labels=True,
                                chart_title=st.session_state.chart_title,
                                color_scheme=st.session_state.color_scheme,
                                font_family=st.session_state.font_family,
                                font_size=st.session_state.font_size,
                                is_3d=st.session_state.is_3d
                            )
                        else:
                            st.error("Please select both X-axis and Y-axis columns to generate the Density Plot.")
    
    
                    elif chart_type == "3D Cone Plot" and st.session_state.x_column and st.session_state.y_column and st.session_state.z_column and st.session_state.u_column and st.session_state.v_column and st.session_state.w_column:
                        st.write("### Chart Preview")
                        context.create_visualization(
                            df,
                            st.session_state.x_column,
                            [st.session_state.u_column, st.session_state.v_column, st.session_state.w_column], 
                            st.session_state.z_column,
                            show_legend=False,
                            show_labels=True,
                            chart_title=st.session_state.chart_title,
                            font_family=st.session_state.font_family,
                            font_size=st.session_state.font_size
                        )
                        
    
                    elif chart_type == "Streamline Plot" and st.session_state.x_column and st.session_state.y_columns and st.session_state.z_column:
                        st.write("### Chart Preview")
                        context.create_visualization(
                            df,
                            st.session_state.x_column,
                            st.session_state.y_columns,
                            st.session_state.z_column,
                            show_legend=False,
                            show_labels=True,
                            chart_title=st.session_state.chart_title,
                            font_family=st.session_state.font_family,
                            font_size=st.session_state.font_size
                        )
    
        else:
            st.warning("No dataset available for visualization. Please ensure you've completed the preprocessing step and saved the dataset.")

data_visualization_page()