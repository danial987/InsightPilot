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