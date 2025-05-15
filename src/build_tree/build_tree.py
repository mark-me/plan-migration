import igraph as ig
import polars as pl

class PlanningTree:
    def __init__(self):
        self.sources = {}
        self.products = {}

    def add_product_sources(self, df_product_sources: pl.DataFrame):
        source_systems = df_product_sources.select("source_systems").unique().to_dicts()
        products = df_product_sources.select(["id_product", "name_product", "status"]).unique().to_dicts()
        pass
