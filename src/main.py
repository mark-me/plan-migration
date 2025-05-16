from pathlib import Path

from importer import ProductFile
from build_tree import PlanningTree

if __name__ == "__main__":
    product_file = ProductFile(path_file=Path("product_sources.xlsx"))
    plan_tree = PlanningTree()
    plan_tree.add_product_sources(df_product_sources=product_file.product_sources)