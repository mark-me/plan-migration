from pathlib import Path

from dashboard import Dash, dcc, html
import plotly.express as px
import polars as pl

from dependencies import PlanningReport
from importers import ProductFile, StatusFile

product_file = ProductFile(path_file=Path("data/product_sources.xlsx"))
status_file = StatusFile(path_file=Path("data/task_status.xlsx"))
plan_report = PlanningReport(file_task_template=Path("data/tasks.json"))

plan_report.add_product_sources(df_product_sources=product_file.product_sources)
plan_report.add_task_statuses(df_task_status=status_file.task_status)

data_tasks = plan_report.get_tasks()
# data_tasks = data_tasks.group_by(["worked_on", "status"]).len()
data_task_source = (
    data_tasks.filter(pl.col("type_task") == "SOURCE")
    .group_by(["worked_on", "status"])
    .len()
    .sort("worked_on")
)
data_task_product = (
    data_tasks.filter(pl.col("type_task") == "PRODUCT")
    .group_by(["worked_on", "status"])
    .len()
    .sort("worked_on")
)


def get_barchart(data: pl.DataFrame):
    fig_source = px.bar(
        data,
        x="worked_on",
        y="len",
        color="status",
        title="Source tasks",
        labels={"len": "# Tasks", "worked_on": "Source"},
        color_discrete_map = {'done': 'limegreen', 'commited': 'royalblue', "waiting": "lightsteelblue"},
        category_orders={"status": ["done", "commited", "waiting"]},
    )
    return fig_source

fig_source = get_barchart(data=data_task_source)
fig_product = get_barchart(data=data_task_product)

app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Migration Analytics"),
        dcc.Graph(figure=fig_source),
        dcc.Graph(figure=fig_product),
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
