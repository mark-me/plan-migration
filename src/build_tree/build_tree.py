from enum import Enum, auto

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

    def __init__(self):
        """Initializes a new PlanningTree instance.

        Sets up empty dictionaries for sources and products, and an empty list for edges.
        """
        self.sources = {}
        self.products = {}
        self.edges = []

    def add_product_sources(self, df_product_sources: pl.DataFrame):
        """Adds product and source nodes to the planning tree from a DataFrame.

        This method updates the internal sources, products, and edges based on the provided product-source relationships.

        Args:
            df_product_sources (pl.DataFrame): DataFrame containing product and source information.
        """
        self._add_sources(
            sources=df_product_sources.select("source_systems").unique().to_dicts()
        )
        self._add_products(
            products=(
                df_product_sources.select(["id_product", "name_product", "status"])
                .unique()
                .to_dicts()
            )
        )
        self.edges = (
            df_product_sources.select(["source_systems", "id_product"])
            .rename({"source_systems": "source", "id_product": "target"})
            .with_columns(pl.lit(EdgeType.SOURCE_PRODUCT.name).alias("type"))
        ).to_dicts()

        self.create_task_dependencies()

    def _add_sources(self, sources: dict) -> None:
        """Adds source nodes to the planning tree from a dictionary.

        Updates the internal sources dictionary and triggers creation of source tasks.

        Args:
            sources (dict): Dictionary containing source system information.
        """
        self.sources = {source["source_systems"]: source for source in sources}
        self.create_source_tasks()

    def _add_products(self, products: dict) -> None:
        """Adds product nodes to the planning tree from a dictionary.

        Updates the internal products dictionary and triggers creation of product tasks.

        Args:
            products (dict): Dictionary containing product information.
        """
        self.products = {product["id_product"]: product for product in products}
        self.create_product_tasks()

    def create_source_tasks(self) -> None:
        """Creates task nodes associated with each source in the planning tree.

        This method is intended to generate and add task nodes for all sources currently in the tree.
        """
        pass

    def create_product_tasks(self) -> None:
        pass

    def create_task_dependencies(self) -> None:
        pass
