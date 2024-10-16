import copy
import shutil
import uuid
from pathlib import Path
from typing import Dict, Generator, List

from pydantic import BaseModel


class DataFormatter:
    """
    Formats data for ingestion by adding a unique ingestion ID and transforming data
    from different sources, such as CSV strings or Pydantic models into JSON.
    """

    def __init__(self):
        """
        Initializes the DataFormatter instance with a unique ingestion ID.
        """
        self.ingestion_id = uuid.uuid4()

    def _add_ingestion_id(self, data: Dict[str, str]) -> Dict[str, str]:
        """
        Adds the ingestion ID to the provided data dictionary.

        Args:
            data (Dict[str, str]): A dictionary of data to which the ingestion ID will be added.

        Returns:
            Dict[str, str]: A new dictionary containing the original data with an added
            'ingestion_id' field.
        """
        new_data = copy.deepcopy(data)
        new_data["ingestion_id"] = self.ingestion_id

        return new_data

    def from_csv(self, data: str):
        """
        Parses a CSV line into a dictionary with predefined keys and adds an ingestion ID.

        Args:
            data (str): A CSV-formatted string representing a single record.

        Returns:
            Dict[str, str]: A dictionary with keys for 'region', 'origin_coord',
            'destination_coord', 'datetime', and 'datasource', with an added 'ingestion_id'.
        """
        items = data.strip().split(",")

        return self._add_ingestion_id(
            {
                "region": items[0],
                "origin_coord": items[1],
                "destination_coord": items[2],
                "datetime": items[3],
                "datasource": items[4],
            }
        )

    def from_pydantic(self, data: List[BaseModel]) -> Generator:
        """
        Converts a list of Pydantic model instances into dictionaries with an ingestion ID.

        Args:
            data (List[BaseModel]): A list of Pydantic model instances to convert.

        Yields:
            Dict[str, str]: A dictionary representation of each model instance with
            an added 'ingestion_id'.
        """
        for d in data:
            yield self._add_ingestion_id(d.__dict__)

    def generate_ingestion_status(self, data: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Generates a summary status for the ingestion, including the ingestion ID
        and the count of records sent by the invoker.

        Args:
            data (List[Dict[str, str]]): A list of ingested data dictionaries.

        Returns:
            Dict[str, str]: A dictionary with the 'ingestion_id' and 'count' of ingested records.
        """
        return {"ingestion_id": self.ingestion_id, "count": len(data)}


class FileHandler:
    """
    Handles file operations such as reading CSV files, listing files in a directory,
    and moving files to a specified processed folder.
    """

    def __init__(self, dir: str) -> None:
        """
        Initializes the FileHandler with a specified directory path.

        Args:
            dir (str): The directory relative to the base path where files are located.
        """
        self.dir = dir
        self.base_dir_path = Path("/home/user")
        self.path = self.base_dir_path / dir

    def read_csv(self, file: str, has_header=False) -> Generator:
        """
        Reads lines from a CSV file, optionally skipping the header row.

        Args:
            file (str): The name of the CSV file to read.
            has_header (bool, optional): If True, skips the first line of the file
            (header). Defaults to False.

        Yields:
            str: Each line in the CSV file after optional header removal.
        """
        with open(file=self.path / file, mode="r") as lines:
            for line_no, line in enumerate(lines):
                if (has_header and line_no > 0) or (not has_header):  # skip first line
                    yield line

    def list_files(self) -> Generator:
        """
        Lists all CSV files in the directory and its subdirectories.

        Yields:
            Path: Each path object representing a CSV file in the directory.
        """
        return self.path.rglob("*.csv")

    def move_file(self, file: str, processed_folder: str) -> None:
        """
        Moves a specified file to the processed folder.

        Args:
            file (str): The name of the file to move.
            processed_folder (str): The target directory under the base path where
            the file should be moved.

        Side Effects:
            - Creates the processed folder if it doesn't exist.
            - Moves the file to the processed folder.
        """

        file_path = self.path / file
        dst_path = self.base_dir_path / processed_folder
        Path.mkdir(dst_path, exist_ok=True)

        shutil.move(file_path, dst_path.as_posix())

    def move_files(self, files: List[str], processed_folder: str) -> None:
        """
        Moves multiple files to a specified processed folder.

        Args:
            files (List[str]): A list of filenames to move.
            processed_folder (str): The target directory under the base path
            where the files should be moved.

        Side Effects:
            - Creates the processed folder if it doesn't exist.
            - Moves each file in the list to the processed folder.
        """

        for file in files:
            self.move_file(file, processed_folder)
