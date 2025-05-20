from pathlib import Path

import polars as pl


class ProductFile:
    def __init__(self, path_file: Path):
        """Initializes the ProductFile with product data from an Excel file.

        Loads the product data into a DataFrame for further processing and analysis.

        Args:
            path_file (Path): Path to the Excel file containing product data.
        """
        df = pl.read_excel(source=path_file)
        self.df_products = df.with_columns(
            pl.col("id_product").cast(pl.Utf8).alias("id_product"))

    @property
    def products(self) -> pl.DataFrame:
        """Returns a DataFrame containing product information.

        The DataFrame includes the product ID, name, and status for each product.

        Returns:
            pl.DataFrame: DataFrame with columns 'id_product', 'name_product', and 'status_product'.
        """
        return self.df_products.select(["id_product", "name_product", "status_product"])

    @property
    def product_sources(self) -> pl.DataFrame:
        """Returns a DataFrame with products and their associated source systems.

        The DataFrame expands the source systems column so each row represents a single product-source relationship.

        Returns:
            pl.DataFrame: DataFrame with products and their corresponding source systems.
        """
        df = (
            self.df_products.with_columns(pl.col("source_systems").str.split("|"))
            .explode("source_systems")
            .with_columns(pl.col("source_systems").str.strip_chars())
        )
        return df

    @property
    def sources(self) -> pl.DataFrame:
        """Returns a DataFrame containing unique source systems.

        The DataFrame includes a single column with all unique source system names extracted from the products data.

        Returns:
            pl.DataFrame: DataFrame with a single column 'source_systems' listing unique sources.
        """
        df = (
            self.df_products.with_columns(pl.col("source_systems").str.split("|"))
            .explode("source_systems")
            .with_columns(pl.col("source_systems").str.strip_chars())
            .select("source_systems")
            .unique()
        )
        return df
