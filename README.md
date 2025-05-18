# Migration planning

Data migration planning and progress report tool. Orchestrates the import of source systems, product and task status data, processes this data using a planning report component, and generates various detail output files (HTML visualizations and an Excel export).

It consists of two modules, one started by running the `src/main.py` file, with the following sequence. This reports on the detailed task dependencies for migrating the ETL of source systems to products.

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

The second part serves a management dashboard by running `src/dashboard/app.py` which is served on [http://127.0.0.1:8050/](http://127.0.0.1:8050/).

The sequence diagram is:

```mermaid
sequenceDiagram
    actor User
    participant MainScript as main.py
    participant ProductFile
    participant StatusFile
    participant PlanningReport

    User->>MainScript: Run script
    MainScript->>ProductFile: Load product_sources.xlsx
    ProductFile-->>MainScript: product_sources DataFrame
    MainScript->>PlanningReport: Initialize with tasks.json
    MainScript->>PlanningReport: add_product_sources(product_sources)
    MainScript->>PlanningReport: plot_tasks_template()
    MainScript->>PlanningReport: plot_source_products()
    MainScript->>PlanningReport: plot_source_product_tasks()
    MainScript->>PlanningReport: export_tasks()
    MainScript->>StatusFile: Load task_status.xlsx
    StatusFile-->>MainScript: task_status DataFrame
    MainScript->>PlanningReport: add_task_statuses(task_status)
    MainScript->>PlanningReport: plot_graph_total_status()
    MainScript->>PlanningReport: plot_graph_product_status(id_product)
    MainScript->>PlanningReport: plot_graph_source_status(id_source)
```