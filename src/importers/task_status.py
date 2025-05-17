from pathlib import Path

import polars as pl

class StatusFile:
    """Handles loading and accessing task status data from an Excel file.

    This class reads task status information from a specified file and provides access to it as a DataFrame.
    """

    def __init__(self, path_file: Path):
        """Initializes the StatusFile by loading task status data from an Excel file.

        Args:
            path_file (Path): Path to the Excel file containing task status data.
        """
        self.df_task_status = pl.read_excel(source=path_file)

    @property
    def task_status(self) -> pl.DataFrame:
        """Returns the loaded task status data as a DataFrame.

        This property provides access to the task status information read from the Excel file.

        Returns:
            pl.DataFrame: The DataFrame containing task status data.
        """
        return self.df_task_status