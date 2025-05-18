import sys
from pathlib import Path

from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl

from dependencies import PlanningReport
from importers import ProductFile, StatusFile

LEGEND_COLORS = {
    "done": "#008000",
    "committed": "royalblue",
    "waiting": "lightsteelblue",
    "ready": "violet",
}

CATEGORY_ORDER = {"status": ["done", "committed", "ready", "waiting"]}


def get_report_data() -> pl.DataFrame:
    """Loads and processes product, source, and task status data for the planning dashboard.

    Reads data from Excel and JSON files, initializes the planning report, and returns a DataFrame of tasks with their statuses.

    Returns:
        pl.DataFrame: A DataFrame containing all tasks and their statuses for reporting.
    """
    path_products = Path("data/product_sources.xlsx")
    if path_products.exists():
        product_file = ProductFile(path_file=path_products)
    else:
        print(f"No product file '{path_products}' found.")
        sys.exit(1)
    path_task_status = Path("data/task_status.xlsx")

    # Load task status data from Excel file
    path_task_status = Path("data/task_status.xlsx")
    if path_task_status.exists():
        status_file = StatusFile(path_file=path_task_status)
    else:
        print(f"No task status file '{path_task_status}' found.")
        sys.exit(1)

    # Initialize the planning report with the task template JSON
    path_tasks = Path("data/tasks.json")
    if path_tasks.exists():
        plan_report = PlanningReport(file_task_template=path_tasks)
    else:
        print(f"No task template file '{path_tasks}' found.")
        sys.exit(1)

    plan_report.add_product_sources(df_product_sources=product_file.product_sources)
    plan_report.add_task_statuses(df_task_status=status_file.task_status)
    return plan_report.get_tasks()


data_tasks = get_report_data()


def get_overall_chart(data: pl.DataFrame):
    """Generates a bar chart showing the total number of tasks by status.

    Groups all tasks by status and returns a Plotly bar chart for overall task progress.

    Args:
        data (pl.DataFrame): The DataFrame containing task data.

    Returns:
        plotly.graph_objs._figure.Figure: The generated overall bar chart figure.
    """
    data = data_tasks.group_by(["status"]).len()
    data = data.with_columns(x=pl.lit("Total"))
    fig = px.bar(
        data,
        x="len",
        y="x",
        color="status",
        title="Total number of tasks",
        labels={
            "x": "",
            "len": "",
            "status": "Status",
        },
        color_discrete_map=LEGEND_COLORS,
        category_orders=CATEGORY_ORDER,
        height=250,
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


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    children="Migration progress",
                    style={
                        "textAlign": "center",
                        "color": "#008000",
                        "font-family": "Arial",
                    },
                ),
            ),
        ),
        dcc.Markdown(
            children="Migration tasks with a status for *done*, *committed* (for current sprint), *ready* (all preconditions a done) and *waiting* for pickup in future sprint.",
            style={
                "textAlign": "center",
                "color": "#008000",
                "font-family": "Arial",
            },
        ),
        html.Br(),
        dbc.Row(dbc.Col(draw_overall(data_tasks=data_tasks))),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Products",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        draw_piechart(
                                            data_tasks=data_tasks, type_task="PRODUCT"
                                        )
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        draw_barchart(
                                            data_tasks=data_tasks, type_task="PRODUCT"
                                        )
                                    ],
                                    width=9,
                                ),
                            ]
                        ),
                    ],
                ),
                dcc.Tab(
                    label="Sources",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        draw_piechart(
                                            data_tasks=data_tasks, type_task="SOURCE"
                                        )
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        draw_barchart(
                                            data_tasks=data_tasks, type_task="SOURCE"
                                        )
                                    ],
                                    width=9,
                                ),
                            ]
                        )
                    ],
                ),
            ]
        ),
    ]
)
if __name__ == "__main__":
    app.run(debug=True)
