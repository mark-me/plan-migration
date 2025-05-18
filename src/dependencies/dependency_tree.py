import json
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List

import igraph as ig
import polars as pl


class VertexType(Enum):
    """Enumerates the types of vertices in the graph.

    Provides distinct identifiers for each type of node in the graph, including sources, products and tasks.
    """

    SOURCE = auto()
    PRODUCT = auto()
    TASK = auto()


class EdgeType(Enum):
    """Enumerates the types of edges in the graph.

    Provides distinct identifiers for each type of edge in the graph, representing relationships between sources, products and tasks.
    """

    SOURCE_TASK = auto()
    PRODUCT_TASK = auto()
    SOURCE_PRODUCT = auto()
    TASK_DEPENDENCY = auto()


class PlanningTree:
    def __init__(self, file_task_template: Path):
        """Initializes a new PlanningTree instance.

        Sets up empty dictionaries for sources and products, and an empty list for edges.
        """
        self.sources = {}
        self.products = {}
        self.tasks = {}
        self.edges = []
        with open(file_task_template) as json_data:
            self.template_tasks = json.load(json_data)

    def add_product_sources(self, df_product_sources: pl.DataFrame) -> None:
        """Adds product and source nodes, edges, and tasks to the planning tree from a DataFrame.

        This method updates the planning tree with new sources, products, their relationships, and associated
        tasks based on the provided product-source data.

        Args:
            df_product_sources (pl.DataFrame): DataFrame containing product and source information.
        """
        # Create source system nodes
        self._add_sources(df_product_sources=df_product_sources)
        # Create product nodes
        self._add_products(df_product_sources=df_product_sources)
        # Create edges between source systems and products
        edges = self._add_edges_source_product(df_product_sources=df_product_sources)
        # Add tasks
        for edge in edges:
            id_product = edge["target"]
            id_source = edge["source"]
            tasks = self._fill_task_template(id_source=id_source, id_product=id_product)
            self._add_edges_source_tasks(id_source=id_source, tasks=tasks)
            self._add_edges_product_tasks(id_product=id_product, tasks=tasks)
            self._add_tasks(tasks=tasks)
            self._add_edges(self._extract_dependencies(tasks=tasks))

    def _add_edges(self, edges: List[dict]) -> None:
        """Adds new edges to the planning tree and ensures all edges are unique.

        Extends the internal edge list with new edges and removes any duplicates based on edge content.

        Args:
            edges (List[dict]): List of edge dictionaries to add to the planning tree.
        """
        self.edges.extend(edges)
        seen = set()
        unique = []
        for d in self.edges:
            # Convert the dictionary to a tuple of key-value pairs, sorted to ensure order consistency
            dict_tuple = tuple(sorted(d.items()))
            if dict_tuple not in seen:
                seen.add(dict_tuple)
                unique.append(d)
        self.edges = unique

    def _add_sources(self, df_product_sources: pl.DataFrame) -> None:
        """Adds source system nodes to the planning tree from a DataFrame.

        Updates the internal sources dictionary with unique source systems extracted from the provided DataFrame.

        Args:
            df_product_sources (pl.DataFrame): DataFrame containing product and source information.
        """
        sources = (
            df_product_sources.filter(pl.col("source_systems").is_not_null())
            .select("source_systems")
            .rename({"source_systems": "name"})
            .unique()
            .to_dicts()
        )
        for source in sources:
            source["task_type"] = "SOURCE"
            source["type"] = VertexType.SOURCE.name
        self.sources = {source["name"]: source for source in sources}

    def _add_products(self, df_product_sources: pl.DataFrame) -> None:
        """Adds product nodes to the planning tree from a DataFrame.

        Updates the internal products dictionary with unique products extracted from the provided DataFrame.

        Args:
            df_product_sources (pl.DataFrame): DataFrame containing product and source information.
        """
        products = (
            df_product_sources.select(["id_product", "name_product", "status"])
            .rename({"id_product": "name"})
            .unique()
            .to_dicts()
        )
        for product in products:
            product["type"] = VertexType.PRODUCT.name
        self.products = {product["name"]: product for product in products}

    def _add_tasks(self, tasks: List[dict]) -> None:
        """Adds task nodes to the planning tree from a list of task dictionaries.

        Updates the internal tasks dictionary with new task nodes, setting their type and type_task attributes.

        Args:
            tasks (List[dict]): List of task dictionaries to add to the planning tree.

        Returns:
            None
        """
        task_nodes = [{**task, "name": task["id_task"]} for task in tasks]
        for task in task_nodes:
            task["type"] = VertexType.TASK.name
        self.tasks.update({task["name"]: task for task in task_nodes})

    def _add_edges_source_product(self, df_product_sources: pl.DataFrame) -> List[dict]:
        """Creates and adds edges between source systems and products in the planning tree.

        Extracts unique source-product relationships from the DataFrame and adds them as edges to the planning tree.

        Args:
            df_product_sources (pl.DataFrame): DataFrame containing product and source information.

        Returns:
            List[dict]: List of edge dictionaries representing source-product relationships.
        """
        edges = (
            df_product_sources.select(["source_systems", "id_product"])
            .unique()
            .rename({"source_systems": "source", "id_product": "target"})
            .with_columns(pl.lit(EdgeType.SOURCE_PRODUCT.name).alias("type"))
            .to_dicts()
        )
        self._add_edges(edges)
        return edges

    def _add_edges_source_tasks(self, id_source: str, tasks: List[dict]) -> None:
        """Adds edges between source tasks and the specified source node in the planning tree.

        Creates and adds edges for all tasks of type 'SOURCE' that are associated with the given source identifier.

        Args:
            id_source (str): Identifier for the source system.
            tasks (List[dict]): List of task dictionaries to connect to the source.
        """
        tasks_source = [
            {
                "source": id_source,
                "target": task["id_task"],
                "type": EdgeType.SOURCE_TASK.name,
            }
            for task in tasks
            if task["type_task"] == "SOURCE"
        ]
        self._add_edges(tasks_source)

    def _add_edges_product_tasks(self, id_product: str, tasks: List[dict]) -> None:
        """Adds edges between product tasks and the specified product node in the planning tree.

        Creates and adds edges for all tasks of type 'PRODUCT' that are associated with the given product identifier.

        Args:
            id_product (str): Identifier for the product.
            tasks (List[dict]): List of task dictionaries to connect to the product.
        """
        tasks_product = [
            {
                "source": task["id_task"],
                "target": id_product,
                "type": EdgeType.PRODUCT_TASK.name,
            }
            for task in tasks
            if task["type_task"] == "PRODUCT"
        ]
        self._add_edges(tasks_product)

    def _fill_task_template(self, id_source: str, id_product: int) -> List[dict]:
        """Fills a task template with specific source and product identifiers.

        Generates a list of task dictionaries with updated IDs and dependencies for a given source and product.

        Args:
            id_source (str): Identifier for the source system.
            id_product (int): Identifier for the product.

        Returns:
            List[dict]: List of task dictionaries with updated IDs and dependencies.
        """
        filled_template = []
        id_mapping = {}

        # First pass to build id_mapping
        for task in self.template_tasks:
            prefix = id_source if task["type_task"] == "SOURCE" else str(id_product)
            new_id = f"{prefix}_{task['id_task']}"
            id_mapping[task["id_task"]] = new_id

        # Second pass to update ids and dependencies
        for task in self.template_tasks:
            new_task = task.copy()
            new_task["id_task"] = id_mapping[new_task["id_task"]]
            new_task["related_to"] = (
                self.products[id_product]["name_product"] if new_task["type_task"] == "PRODUCT" else ""
            )
            new_task["depends_on"] = [id_mapping[dep] for dep in new_task["depends_on"]]
            new_task["worked_on"] = (
                id_source if new_task["type_task"] == "SOURCE" else str(id_product)
            )
            filled_template.append(new_task)

        return filled_template

    def _extract_dependencies(self, tasks: List[dict]) -> List[Dict[str, str]]:
        """Extracts task dependency edges from a list of task dictionaries.

        Generates a list of edge dictionaries representing dependencies between tasks based on their 'depends_on' fields.

        Args:
            tasks (List[dict]): List of task dictionaries to extract dependencies from.

        Returns:
            List[Dict[str, str]]: List of edge dictionaries representing task dependencies.
        """
        dependencies = []
        for task in tasks:
            dependencies.extend(
                {
                    "source": dependency,
                    "target": task["id_task"],
                    "type": EdgeType.TASK_DEPENDENCY.name,
                }
                for dependency in task.get("depends_on", [])
            )
        return dependencies

    def add_task_statuses(self, df_task_status: pl.DataFrame) -> None:
        """Updates the status of tasks in the planning tree from a DataFrame.

        This method assigns status values to tasks based on the provided task status data.

        Args:
            df_task_status (pl.DataFrame): DataFrame containing task status information.
        """
        task_statuses = df_task_status.to_dicts()
        for task_status in task_statuses:
            task = task_status["task"]
            self.tasks[task]["status"] = task_status["status"]

    def get_tasks_template(self) -> ig.Graph:
        """Creates and returns a template graph of tasks and their dependencies.

        This method generates a directed graph representing the template tasks and their dependency relationships.

        Returns:
            ig.Graph: A directed igraph Graph object of the template tasks and dependencies.
        """
        vertices = [{**task, "name": task["id_task"]} for task in self.template_tasks]
        for vx in vertices:
            vx["type"] = VertexType.TASK.name
        edges = []
        for task in self.template_tasks:
            edges.extend(
                {
                    "source": dependency,
                    "target": task["id_task"],
                    "type": EdgeType.TASK_DEPENDENCY.name,
                }
                for dependency in task.get("depends_on", [])
            )
        graph = ig.Graph.DictList(vertices=vertices, edges=edges, directed=True)
        return graph

    def get_product_sources(self) -> ig.Graph:
        """Creates and returns a graph of product and source nodes with their relationships.

        This method generates a directed graph representing only the products, sources, and their direct connections.

        Returns:
            ig.Graph: A directed igraph Graph object of products, sources, and their relationships.
        """
        vertices = list(self.sources.values()) + list(self.products.values())
        edges = [
            edge
            for edge in self.edges
            if edge["type"]
            not in [
                EdgeType.TASK_DEPENDENCY.name,
                EdgeType.PRODUCT_TASK.name,
                EdgeType.SOURCE_TASK.name,
            ]
        ]
        graph = ig.Graph.DictList(vertices=vertices, edges=edges, directed=True)
        return graph

    def get_product_source_tasks(self) -> ig.Graph:
        """Creates and returns a graph of all nodes and their dependencies in the planning tree.

        This method generates a directed graph including sources, products, tasks, and all their relationships except source-product edges.

        Returns:
            ig.Graph: A directed igraph Graph object of all nodes and their dependencies.
        """
        vertices = (
            list(self.sources.values())
            + list(self.products.values())
            + list(self.tasks.values())
        )
        edges = [
            edge
            for edge in self.edges
            if edge["type"] not in [EdgeType.SOURCE_PRODUCT.name]
        ]
        graph = ig.Graph.DictList(vertices=vertices, edges=edges, directed=True)
        return graph

    def get_task_graphs(self) -> ig.Graph:
        """Creates and returns a graph of all tasks and their dependencies.

        This method generates a directed graph representing only the tasks and their dependency relationships.

        Returns:
            ig.Graph: A directed igraph Graph object of tasks and their dependencies.
        """
        vertices = list(self.tasks.values())
        edges = [
            edge for edge in self.edges if edge["type"] == EdgeType.TASK_DEPENDENCY.name
        ]
        graph = ig.Graph.DictList(vertices=vertices, edges=edges, directed=True)
        return graph

    def get_product_tasks(self, id_product: str) -> ig.Graph:
        """Returns a subgraph containing the specified product and all its dependencies.

        Extracts and returns a directed graph of the product node and all nodes that are upstream dependencies.

        Args:
            id_product (int): The identifier of the product node to extract dependencies for.

        Returns:
            ig.Graph: A directed igraph Graph object containing the product and its dependencies.
        """
        dag = self.get_product_source_tasks()
        vx_product = dag.vs.select(name=id_product)[0]
        vs = dag.subcomponent(vx_product, mode="in")
        vs_delete = [i for i in dag.vs.indices if i not in vs]
        dag.delete_vertices(vs_delete)
        return dag

    def get_source_tasks(self, id_source: str) -> ig.Graph:
        """Returns a subgraph containing the specified source and all its downstream dependencies.

        Extracts and returns a directed graph of the source node and all nodes that are downstream dependencies.

        Args:
            id_source (str): The identifier of the source node to extract dependencies for.

        Returns:
            ig.Graph: A directed igraph Graph object containing the source and its dependencies.
        """
        dag = self.get_product_source_tasks()
        vx_source = dag.vs.select(name=id_source)[0]
        vs = dag.subcomponent(vx_source, mode="out")
        vs_delete = [i for i in dag.vs.indices if i not in vs]
        dag.delete_vertices(vs_delete)
        return dag

    def set_tasks_ready(self, dag: ig.Graph) -> ig.Graph:
        """Sets the status of tasks to 'ready' if all their task dependencies are marked as 'done'.

        Iterates through all task nodes in the graph and updates their status to 'ready' if all predecessor tasks are completed.

        Args:
            dag (ig.Graph): The igraph Graph object containing tasks and their dependencies.

        Returns:
            ig.Graph: The updated igraph Graph object with task statuses set to 'ready' where appropriate.
        """
        lst_next_up = []
        vs_tasks = dag.vs.select(type_eq=VertexType.TASK.name)
        for vx in vs_tasks:
            if vx["status"] is None:
                vs_predecessors = dag.predecessors(vx)
                statusses = [
                    dag.vs[i]["status"]
                    for i in vs_predecessors
                    if dag.vs[i]["type"] == VertexType.TASK.name
                ]
                if statusses and all(x == "done" for x in statusses):
                    lst_next_up.append(vx)
        for vx in lst_next_up:
            if vx["type"] == VertexType.TASK.name and vx["status"] is None:
                vx["status"] = "ready"
        return dag
