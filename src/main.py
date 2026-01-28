import logging
import yaml
from pathlib import Path

from importers import ProductFile
from importers import StatusFile
from dependencies import PlanningReport
from dashboard import Dashboard

logger = logging.getLogger(__name__)

class DataFileNotFoundError(Exception):
    """Raised when a required data file is not found."""


def load_data(config: dict) -> PlanningReport:
    """Loads product, source, and task status data into a PlanningReport.

    Reads product, source, and task status files as specified in the config, and returns a populated PlanningReport object.

    Args:
        config (dict): Configuration dictionary containing file paths and settings.

    Returns:
        PlanningReport: The populated PlanningReport object with all data loaded.

    Raises:
        DataFileNotFoundError: If any required data file is not found.
    """
    # Load product and source system data from Excel file
    path_products = Path(f"{config["dir_data"]}/{config["file_products"]}")
    if not path_products.exists():
        raise DataFileNotFoundError(f"No product file '{path_products}' found.")

    product_file = ProductFile(path_file=path_products)
    logger.info(f"Product file '{path_products}' loaded.")
    # Initialize the planning report with the task template JSON
    path_tasks = Path(f"{config["dir_data"]}/{config["file_task_template"]}")
    if not path_tasks.exists():
        raise DataFileNotFoundError(f"No product file '{path_products}' found.")

    plan_report = PlanningReport(file_task_template=path_tasks)
    logger.info(f"Task template file '{path_tasks}' loaded.")
    # Add products and sources to the planning report
    plan_report.add_product_sources(df_product_sources=product_file.product_sources)

    # Load task status data from Excel file
    for file_status in config["files_status"]:
        path_task_status = Path(f"{config["dir_data"]}/{file_status}")

        if not path_task_status.exists():
            raise DataFileNotFoundError(f"No product file '{path_products}' found.")

        status_file = StatusFile(path_file=path_task_status)
        logger.info(f"Task status file '{path_task_status}' loaded.")
        # Add task statuses to the planning report
        plan_report.add_task_statuses(df_task_status=status_file.task_status)

    return plan_report

def _load_config(path: str = "config.yml") -> dict:
    """Load configuration from a YAML file."""
    with open(path, encoding="utf-8") as file:
        return yaml.safe_load(file)


def _plot_task_templates(plan_report: PlanningReport, dir_output: str) -> None:
    """Plot and save task template-related visualizations."""
    file_output = f"{dir_output}/tasks_template.html"
    plan_report.plot_tasks_template(file_html=file_output)
    logger.info(f"Task template visualized in '{file_output}'.")


def _plot_dependencies(plan_report: PlanningReport, dir_output: str) -> None:
    """Plot and save dependency graphs."""
    file_output = f"{dir_output}/source_products.html"
    plan_report.plot_source_products(file_html=file_output)
    logger.info(f"Source product combinations visualized in '{file_output}'.")

    file_output = f"{dir_output}/all.html"
    plan_report.plot_source_product_tasks(file_html=file_output)
    logger.info(f"Source product combinations visualized in '{file_output}'.")


def _plot_status_graphs(plan_report: PlanningReport, config: dict) -> None:
    """Plot and save task status-related graphs."""
    dir_output = config["dir_output"]

    file_output = f"{dir_output}/all_task_status.html"
    plan_report.plot_graph_total_status(file_html=file_output)
    logger.info(f"All tasks with their status visualized in '{file_output}'.")

    file_output = f"{dir_output}/product.html"
    plan_report.plot_graph_product_status(
        id_product=config["inspect_product"], file_html=file_output
    )
    logger.info(
        f"Product task flow for product {config['inspect_product']} visualized in '{file_output}'."
    )


def _export_tasks(plan_report: PlanningReport, dir_output: str) -> None:
    """Export all tasks to an Excel file."""
    file_output = f"{dir_output}/tasks.xlsx"
    plan_report.export_tasks(file_xlsx=file_output)
    logger.info(f"Tasks exported to '{file_output}'.")


def _generate_reports(plan_report: PlanningReport, config: dict) -> None:
    """Generate all plots and exports based on the planning report and config."""
    dir_output = config["dir_output"]
    _plot_task_templates(plan_report=plan_report, dir_output=dir_output)
    _plot_dependencies(plan_report=plan_report, dir_output=dir_output)
    _plot_status_graphs(plan_report=plan_report, config=config)
    _export_tasks(plan_report=plan_report, dir_output=dir_output)


def _start_dashboard(plan_report: PlanningReport) -> None:
    """Start the dashboard application."""
    app = Dashboard(df_tasks_status=plan_report.get_tasks())
    app.start()


def main():
    """Runs the main workflow for loading data, generating reports, and starting the dashboard.

    Loads configuration, processes data, generates visualizations and exports, and launches the dashboard application.
    """
    config = _load_config()
    plan_report = load_data(config=config)
    _generate_reports(plan_report=plan_report, config=config)
    _start_dashboard(plan_report=plan_report)

if __name__ == "__main__":
    main()


