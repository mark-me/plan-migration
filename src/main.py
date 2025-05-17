from pathlib import Path

from importers import ProductFile
from importers import StatusFile
from dependencies import PlanningReport

if __name__ == "__main__":
    product_file = ProductFile(path_file=Path("data/product_sources.xlsx"))
    status_file = StatusFile(path_file=Path("data/task_status.xlsx"))
    plan_report = PlanningReport(file_task_template=Path("data/tasks.json"))

    plan_report.add_product_sources(df_product_sources=product_file.product_sources)
    plan_report.plot_tasks_template(file_html="output/tasks_template.html")
    plan_report.plot_source_products(file_html="output/source_products.html")
    plan_report.plot_source_product_tasks(file_html="output/all.html")
    plan_report.export_tasks(file_xlsx="output/tasks.xlsx")

    plan_report.add_task_statuses(df_task_status=status_file.task_status)
    plan_report.plot_graph_total_status(file_html="output/task_status.html")

    plan_report.plot_graph_product_status(id_product=12355, file_html="output/product.html")
    plan_report.plot_graph_source_status(id_source="DMS", file_html="output/source.html")