import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl
from dash import dcc, html

LEGEND_COLORS = {
    "done": "#008000",
    "committed": "royalblue",
    "waiting": "lightsteelblue",
    "ready": "violet",
}

CATEGORY_ORDER = {"status": ["done", "committed", "ready", "waiting"]}


def get_overall_chart(data: pl.DataFrame):
    """Generates a bar chart showing the total number of tasks by status.

    Groups all tasks by status and returns a Plotly bar chart for overall task progress.

    Args:
        data (pl.DataFrame): The DataFrame containing task data.

    Returns:
        plotly.graph_objs._figure.Figure: The generated overall bar chart figure.
    """
    data = data.group_by(["status"]).len().with_columns(x=pl.lit("Total"))
    fig = px.bar(
        data,
        x="len",
        y="x",
        color="status",
        title="All source and product related tasks",
        labels={
            "x": "",
            "len": "",
            "status": "Status",
        },
        color_discrete_map=LEGEND_COLORS,
        category_orders=CATEGORY_ORDER,
        height=225,
        text_auto=True,
    )
    fig.update_layout(
        font_family="Arial",
        font_color="#008000",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(showticklabels=False)
    return fig


def get_pie_chart(data_tasks: pl.DataFrame, type_task: str):
    """Generates a pie chart showing the percentage of tasks by status for a given task type.

    Filters the data for the specified task type, groups by status, and returns a Plotly pie chart.

    Args:
        data_tasks (pl.DataFrame): The DataFrame containing task data.
        type_task (str): The type of task to filter for (e.g., "SOURCE" or "PRODUCT").

    Returns:
        plotly.graph_objs._figure.Figure: The generated pie chart figure.
    """
    data = (
        data_tasks.filter(pl.col("type_task") == type_task).group_by(["status"]).len()
    )
    fig = px.pie(
        data,
        values="len",
        names="status",
        color="status",
        title="Percentage of tasks",
        color_discrete_map=LEGEND_COLORS,
        category_orders=CATEGORY_ORDER,
    )
    fig.update_layout(
        font_family="Arial",
        font_color="#008000",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1.1),
    )
    return fig


def get_bar_chart(data: pl.DataFrame, type_task: str):
    """Generates a bar chart of task counts by status and group.

    Filters the data for the specified task type, groups by 'worked_on' and 'status', and returns a Plotly bar chart.

    Args:
        data (pl.DataFrame): The DataFrame containing task data.
        type_task (str): The type of task to filter for (e.g., "SOURCE" or "PRODUCT").

    Returns:
        plotly.graph_objs._figure.Figure: The generated bar chart figure.
    """
    data = (
        data.filter(pl.col("type_task") == type_task)
        .group_by(["worked_on", "status"])
        .len()
        .sort("worked_on")
    )
    fig = px.bar(
        data,
        x="worked_on",
        y="len",
        color="status",
        labels={
            "len": "# Tasks",
            "worked_on": type_task.capitalize(),
            "status": "Status",
        },
        color_discrete_map=LEGEND_COLORS,
        category_orders=CATEGORY_ORDER,
    )
    fig.update_layout(
        font_family="Arial",
        font_color="#008000",
        legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="right", x=1),
    )
    fig.update_xaxes(categoryorder="category ascending")
    return fig


def draw_overall(data_tasks: pl.DataFrame) -> html.Div:
    """Creates a Dash HTML component containing an overall bar chart of task statuses.

    Wraps the overall status bar chart in a styled card for display in the dashboard layout.

    Args:
        data_tasks (pl.DataFrame): The DataFrame containing task data.

    Returns:
        html.Div: A Dash HTML Div containing the overall bar chart card.
    """
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            figure=get_overall_chart(data=data_tasks),
                            config={"displayModeBar": False},
                        )
                    ]
                )
            )
        ]
    )


def draw_barchart(data_tasks: pl.DataFrame, type_task: str) -> html.Div:
    """Creates a Dash HTML component containing a bar chart of tasks by status and group.

    Wraps the generated bar chart in a styled card for display in the dashboard layout.

    Args:
        data_tasks (pl.DataFrame): The DataFrame containing task data.
        type_task (str): The type of task to filter for (e.g., "SOURCE" or "PRODUCT").

    Returns:
        html.Div: A Dash HTML Div containing the bar chart card.
    """
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            figure=get_bar_chart(data=data_tasks, type_task=type_task),
                            config={"displayModeBar": False},
                        )
                    ]
                )
            )
        ]
    )


def draw_piechart(data_tasks: pl.DataFrame, type_task: str) -> html.Div:
    """Creates a Dash HTML component containing a pie chart of task statuses for a given task type.

    Wraps the generated pie chart in a styled card for display in the dashboard layout.

    Args:
        data_tasks (pl.DataFrame): The DataFrame containing task data.
        type_task (str): The type of task to filter for (e.g., "SOURCE" or "PRODUCT").

    Returns:
        html.Div: A Dash HTML Div containing the pie chart card.
    """
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            figure=get_pie_chart(
                                data_tasks=data_tasks, type_task=type_task
                            ),
                            config={"displayModeBar": False},
                        )
                    ]
                )
            )
        ]
    )
