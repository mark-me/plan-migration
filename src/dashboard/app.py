import sys
from pathlib import Path

from dash import Dash, dcc, html
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
    fig_source = px.bar(
        data,
        x="worked_on",
        y="len",
        color="status",
        title=f"{type_task.capitalize()} tasks",
        labels={"len": "# Tasks", "worked_on": "Source"},
        color_discrete_map={
            "done": "limegreen",
            "commited": "royalblue",
            "waiting": "lightsteelblue",
        },
        category_orders={"status": ["done", "commited", "waiting"]},
    )
    return fig_source


app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Migration Analytics"),
        dcc.Graph(figure=get_barchart(data=data_tasks, type_task="SOURCE")),
        dcc.Graph(figure=get_barchart(data=data_tasks, type_task="PRODUCT")),
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
