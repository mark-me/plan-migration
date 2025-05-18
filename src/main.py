import sys
from pathlib import Path

from importers import ProductFile
from importers import StatusFile
from dependencies import PlanningReport

if __name__ == "__main__":
    # Load product and source system data from Excel file
    path_products = Path("data/product_sources.xlsx")
    if path_products.exists():
        product_file = ProductFile(path_file=path_products)
    else:
        print(f"No product file '{path_products}' found.")
        sys.exit(1)

    # Initialize the planning report with the task template JSON
    path_tasks = Path("data/tasks.json")
    if path_tasks.exists():
        plan_report = PlanningReport(file_task_template=path_tasks)
    else:
        print(f"No task template file '{path_tasks}' found.")
        sys.exit(1)

    # Add products and sources to the planning report
    plan_report.add_product_sources(df_product_sources=product_file.product_sources)
    # Plot the template of all tasks and save as HTML
    plan_report.plot_tasks_template(file_html="output/tasks_template.html")
    # Plot the source-product dependency graph and save as HTML
    plan_report.plot_source_products(file_html="output/source_products.html")
    # Plot the full source-product-task dependency graph and save as HTML
    plan_report.plot_source_product_tasks(file_html="output/all.html")

    # Load task status data from Excel file
    path_task_status = Path("data/task_status.xlsx")
    if path_task_status.exists():
        status_file = StatusFile(path_file=path_task_status)
    else:
        print(f"No task status file '{path_task_status}' found.")
        sys.exit(1)
    # Add task statuses to the planning report
    plan_report.add_task_statuses(df_task_status=status_file.task_status)
    # Plot the full graph with task statuses and save as HTML
    plan_report.plot_graph_total_status(file_html="output/task_status.html")

    # Plot the status graph for a specific product and save as HTML
    plan_report.plot_graph_product_status(id_product="12355", file_html="output/product.html")
    # Plot the status graph for a specific source and save as HTML
    plan_report.plot_graph_source_status(id_source="DMS", file_html="output/source.html")

    # Export all tasks to an Excel file
    plan_report.export_tasks(file_xlsx="output/tasks.xlsx")