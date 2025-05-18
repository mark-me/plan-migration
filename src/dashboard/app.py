import sys
from pathlib import Path

from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl

from dependencies import PlanningReport
from importers import ProductFile, StatusFile

# Load product and source system data from Excel file
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

data_tasks = plan_report.get_tasks()


def get_overall(data: pl.DataFrame):
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
        color_discrete_map={
            "done": "#008000",
            "commited": "royalblue",
            "waiting": "lightsteelblue",
        },
        category_orders={"status": ["done", "commited", "waiting"]},
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


def draw_overall(data_tasks: pl.DataFrame) -> html.Div:
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            figure=get_overall(data=data_tasks),
                            config={"displayModeBar": False},
                        )
                    ]
                )
            )
        ]
    )


def get_barchart(data: pl.DataFrame, type_task: str):
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
        # title=f"{type_task.capitalize()} tasks",
        labels={
            "len": "# Tasks",
            "worked_on": type_task.capitalize(),
            "status": "Status",
        },
        color_discrete_map={
            "done": "#008000",
            "commited": "royalblue",
            "waiting": "lightsteelblue",
        },
        category_orders={"status": ["done", "commited", "waiting"]},
    )
    fig.update_layout(font_family="Arial", font_color="#008000")
    fig.update_xaxes(categoryorder="category ascending")
    return fig


def draw_barchart(data_tasks: pl.DataFrame, type_task: str) -> html.Div:
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            figure=get_barchart(data=data_tasks, type_task=type_task),
                            config={"displayModeBar": False},
                        )
                    ]
                )
            )
        ]
    )


def get_piechart(data_tasks: pl.DataFrame, type_task: str):
    data = (
        data_tasks.filter(pl.col("type_task") == type_task).group_by(["status"]).len()
    )
    fig = px.pie(
        data,
        values="len",
        names="status",
        color="status",
        title="Percentage of tasks",
        color_discrete_map={
            "done": "#008000",
            "commited": "royalblue",
            "waiting": "lightsteelblue",
        },
        category_orders={"status": ["done", "commited", "waiting"]},
    )
    fig.update_layout(
        font_family="Arial",
        font_color="#008000",
    )
    return fig


def draw_piechart(data_tasks: pl.DataFrame, type_task: str) -> html.Div:
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            figure=get_piechart(
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
                )
            )
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
