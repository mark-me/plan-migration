from pathlib import Path

import polars as pl


class ProductFile:
    def __init__(self, path_file: Path):
        self.df_products = pl.read_excel(source=path_file)

    @property
    def products(self) -> pl.DataFrame:
        return self.df_products.select(["id_product", "name_product", "status"])

    @property
    def product_sources(self) -> pl.DataFrame:
        df = (
            self.df_products.with_columns(pl.col("source_systems").str.split("|"))
            .explode("source_systems")
            .with_columns(pl.col("source_systems").str.strip_chars())
        )
        return df

    @property
    def sources(self) -> pl.DataFrame:
        df = (
            self.df_products.with_columns(pl.col("source_systems").str.split("|"))
            .explode("source_systems")
            .with_columns(pl.col("source_systems").str.strip_chars())
            .select("source_systems")
            .unique()
        )
        return df


if __name__ == "__main__":
    product_file = ProductFile(Path("product_sources.xlsx"))
    df = product_file.product_sources
    df
