# Migration planning

Data migration planning and progress report tool. Orchestrates the import of source systems, product and task status data, processes this data using a planning report component, and generates various detailed output files (HTML visualizations and an Excel export).

The `src/main.py` file serves as the main entry point for a data processing and visualization pipeline related to planning and task management. It orchestrates the loading of configuration and data files, processes and aggregates planning information, generates various visualizations and reports, and finally launches an interactive dashboard on [http://127.0.0.1:8050/](http://127.0.0.1:8050/) for further exploration.
