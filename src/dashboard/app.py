import dash_bootstrap_components as dbc
import polars as pl
from dash import Dash, dcc, html

from .charts import draw_bar_chart, draw_overall, draw_pie_chart, draw_bar_polar_chart


class Dashboard:
    def __init__(self, df_tasks_status: pl.DataFrame):
        self.data_tasks = df_tasks_status
        self.app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.set_layout()

    def set_layout(self):
        self.app.layout = html.Div(
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
                dbc.Row(dbc.Col(draw_overall(data_tasks=self.data_tasks))),
                dcc.Tabs(
                    [
                        dcc.Tab(
                            label="Products",
                            children=[
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                draw_pie_chart(
                                                    data_tasks=self.data_tasks,
                                                    type_task="PRODUCT",
                                                )
                                            ],
                                            width=3,
                                        ),
                                        dbc.Col(
                                            [
                                                draw_bar_polar_chart(
                                                    data_tasks=self.data_tasks,
                                                    type_task="PRODUCT",
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
                                                draw_pie_chart(
                                                    data_tasks=self.data_tasks,
                                                    type_task="SOURCE",
                                                )
                                            ],
                                            width=3,
                                        ),
                                        dbc.Col(
                                            [
                                                draw_bar_polar_chart(
                                                    data_tasks=self.data_tasks,
                                                    type_task="SOURCE",
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

    def start(self, debug: bool = False):
        self.app.run(debug=debug)
