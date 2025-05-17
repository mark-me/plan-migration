import os
from pathlib import Path

import igraph as ig
import networkx as nx
from pyvis.network import Network

from .dependency_tree import PlanningTree, VertexType, EdgeType


class PlanningReport(PlanningTree):
    def __init__(self):
        super().__init__()
        self.node_type_shape = {
            VertexType.SOURCE.name: "database",
            VertexType.TASK.name: "square",
            VertexType.PRODUCT.name: "hexagon"
        }
        self.node_type_color = {
            VertexType.SOURCE.name: "#fbed8f",
            VertexType.TASK.name: "#73c4e5",
            VertexType.PRODUCT.name: "#8962ad"
        }

    def _create_output_dir(self, file_path: str) -> None:
        parent_directory = os.path.dirname(file_path)
        Path(parent_directory).mkdir(parents=True, exist_ok=True)

    def _igraph_to_networkx(self, graph: ig.Graph) -> nx.DiGraph:
        """Converts an igraph into a networkx graph

        Args:
            dag (ig.Graph): igraph graph

        Returns:
            nx.DiGraph: networkx graph
        """
        dag_nx = nx.DiGraph()
        # Convert nodes
        lst_nodes_igraph = graph.get_vertex_dataframe().to_dict("records")
        lst_nodes = []
        lst_nodes.extend((node["name"], node) for node in lst_nodes_igraph)
        dag_nx.add_nodes_from(lst_nodes)

        # Convert edges
        lst_edges_igraph = graph.get_edge_dataframe().to_dict("records")
        lst_edges = []
        lst_edges.extend((edge["source"], edge["target"]) for edge in lst_edges_igraph)
        dag_nx.add_edges_from(lst_edges)
        return dag_nx

    def _set_node_tooltip(self, node: ig.Vertex) -> None:
        if node["type"] == VertexType.SOURCE.name:
            node["title"] = f"""System: {node["name"]}"""
        elif node["type"] == VertexType.PRODUCT.name:
            node["title"] = f"""ID: {node["name"]}
                        Name: {node["name_product"]}
                        Status: {node["status"]}
                    """
        elif node["type"] == VertexType.TASK.name:
            node["title"] = f"""ID: {node["name"]}
                        Description: {node["description"]}
                        Type: {node["type_task"]}
                    """

    def _set_visual_attributes(self, dag: ig.Graph) -> ig.Graph:
        """Set attributes for pyvis visualization.

        Sets the shape, shadow, color, and tooltip for each node in the graph
        based on their type and other properties.

        Args:
            graph (ig.Graph): The igraph graph to set attributes for.

        Returns:
            ig.Graph: The graph with attributes set for pyvis visualization.
        """
        for node in dag.vs:
            node["shape"] = self.node_type_shape[node["type"]]
            node["shadow"] = True
            if node["type"] == VertexType.TASK.name:
                node["color"] = self.node_type_color[node["type_task"]]
            else:
                node["color"] = self.node_type_color[node["type"]]
            self._set_node_tooltip(node)
        return dag

    def plot_graph_html(self, dag: ig.Graph, file_html: str) -> None:
        """Create a html file with a graphical representation of a networkx graph

        Args:
            dag (nx.DiGraph): Networkx DAG
            file_html_out (str): file path that the result should be written to
        """
        self._create_output_dir(file_path=file_html)
        net = Network("900px", "1917px", directed=True, layout=True)
        dag = self._igraph_to_networkx(graph=dag)
        net.from_nx(dag)
        net.options.layout.hierarchical.sortMethod = "directed"
        net.options.physics.solver = "hierarchicalRepulsion"
        net.options.edges.smooth = False
        net.options.interaction.navigationButtons = True
        net.toggle_physics(True)
        for edge in net.edges:
            edge["shadow"] = True
        net.write_html(file_html, notebook=False)

    def plot_tasks_template(self, file_html: str) -> None:
        dag = self.get_tasks_template()
        dag = self._set_visual_attributes(dag=dag)
        self.plot_graph_html(dag=dag, file_html=file_html)

    def plot_source_products(self, file_html: str) -> None:
        dag = self.get_product_sources()
        dag = self._set_visual_attributes(dag=dag)
        self.plot_graph_html(dag=dag, file_html=file_html)

    def plot_graph_total(self, file_html: str) -> None:
        """Plot the total graph and save it to an HTML file.

        Builds the total graph, sets pyvis attributes, and visualizes it in an HTML file.

        Args:
            file_html (str): The path to the HTML file where the plot will be saved.

        Returns:
            None
        """
        dag = self.get_dependencies_total()
        dag = self._set_visual_attributes(dag=dag)
        self.plot_graph_html(dag=dag, file_html=file_html)