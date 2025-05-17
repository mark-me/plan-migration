from pathlib import Path

from importer import ProductFile
from dependencies import PlanningReport

if __name__ == "__main__":
    product_file = ProductFile(path_file=Path("product_sources.xlsx"))
    plan_report = PlanningReport()
    plan_report.add_product_sources(df_product_sources=product_file.product_sources)
    plan_report.plot_tasks_template(file_html="output/tasks_template.html")
    plan_report.plot_source_products(file_html="output/source_products.html")
    plan_report.plot_graph_total(file_html="output/all.html")