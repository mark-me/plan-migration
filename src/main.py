import logging
import sys
import yaml
from pathlib import Path

from importers import ProductFile
from importers import StatusFile
from dependencies import PlanningReport
from dashboard import Dashboard

logger = logging.getLogger(__name__)

def load_data(config: dict) -> PlanningReport:
    # Load product and source system data from Excel file
    path_products = Path(f"{config["dir_data"]}/{config["file_products"]}")
    if path_products.exists():
        product_file = ProductFile(path_file=path_products)
        logger.info(f"Product file '{path_products}' loaded.")
    else:
        logger.error(f"No product file '{path_products}' found.")
        sys.exit(1)

    # Initialize the planning report with the task template JSON
    path_tasks = Path(f"{config["dir_data"]}/{config["file_task_template"]}")
    if path_tasks.exists():
        plan_report = PlanningReport(file_task_template=path_tasks)
        logger.info(f"Task template file '{path_tasks}' loaded.")
    else:
        logger.error(f"No task template file '{path_tasks}' found.")
        sys.exit(1)

    # Add products and sources to the planning report
    plan_report.add_product_sources(df_product_sources=product_file.product_sources)

    # Load task status data from Excel file
    for files_status in config["file_statusses"]:
        path_task_status = Path(f"{config["dir_data"]}/{files_status}")

        if path_task_status.exists():
            status_file = StatusFile(path_file=path_task_status)
            logger.info(f"Task status file '{path_task_status}' loaded.")
        else:
            logger.error(f"No task status file '{path_task_status}' found.")
            sys.exit(1)

        # Add task statuses to the planning report
        plan_report.add_task_statuses(df_task_status=status_file.task_status)

    return plan_report

def main():
    with open("config.yml", encoding="utf-8") as file:
        config = yaml.load(file, Loader=yaml.Loader)
    plan_report = load_data(config=config)

    # Plot the template of all tasks and save as HTML
    file_output = f"{config["dir_output"]}/tasks_template.html"
    plan_report.plot_tasks_template(file_html=file_output)
    logger.info(f"Task template visualized in '{file_output}'.")

    # Plot the source-product dependency graph and save as HTML
    file_output = f"{config["dir_output"]}/source_products.html"
    plan_report.plot_source_products(file_html=file_output)
    logger.info(f"Source product combinations visualized in '{file_output}'.")

    # Plot the full source-product-task dependency graph and save as HTML
    file_output = f"{config["dir_output"]}/all.html"
    plan_report.plot_source_product_tasks(file_html=file_output)
    logger.info(f"Source product combinations visualized in '{file_output}'.")

    # Plot the full graph with task statuses and save as HTML
    file_output = f"{config["dir_output"]}/all_task_status.html"
    plan_report.plot_graph_total_status(file_html=file_output)
    logger.info(f"All tasks with their status visualized in '{file_output}'.")

    # Plot the status graph for a specific product and save as HTML
    file_output = f"{config["dir_output"]}/product.html"
    plan_report.plot_graph_product_status(id_product=config["inspect_product"], file_html=file_output)
    logger.info(f"Product task flow for product {config["inspect_product"]} visualized in '{file_output}'.")

    # Export all tasks to an Excel file
    file_output = f"{config["dir_output"]}/tasks.html"
    plan_report.export_tasks(file_xlsx=file_output)
    logger.info(f"Task status in total overview visualized in '{file_output}'.")

    # Start dashboard
    app = Dashboard(df_tasks_status=plan_report.get_tasks())
    app.start()

if __name__ == "__main__":
    main()


