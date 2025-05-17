# Migration planning

Data migration planning and progress report tool.  Orchestrates the import of product and status data, processes this data using a planning report component, and generates various output files (HTML visualizations and an Excel export).

```mermaid
sequenceDiagram
    participant MainScript
    participant ProductFile
    participant StatusFile
    participant PlanningReport

    MainScript->>ProductFile: Instantiate with product_sources.xlsx
    MainScript->>StatusFile: Instantiate with task_status.xlsx
    MainScript->>PlanningReport: Instantiate with tasks.json
    MainScript->>PlanningReport: add_product_sources(product_sources)
    MainScript->>PlanningReport: plot_tasks_template(tasks_template.html)
    MainScript->>PlanningReport: plot_source_products(source_products.html)
    MainScript->>PlanningReport: plot_graph_total(all.html)
    MainScript->>PlanningReport: export_tasks(tasks.xlsx)
    MainScript->>PlanningReport: add_task_statuses(task_status)
```
