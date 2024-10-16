from google.cloud import bigquery
from models import Square
from typing import List


class BigQueryService:
    """
    Provides methods for interacting with Google BigQuery, including running queries
    on geographic data to calculate trip statistics.
    """

    def __init__(self):
        """
        Initializes the BigQueryService instance with a BigQuery client.
        """
        self.__client = bigquery.Client()

    def get_average_trips_by_area(
        self, project_id: str, dataset_id: str, table_id: str, square: Square
    ) -> List[bigquery.Row]:
        """
        Retrieves the weekly average count of trips occurring within a specified geographic area.

        This method constructs a SQL query to count trips that start and end within a
        defined rectangular region, grouped by weekly intervals.

        Args:
            project_id (str): The Google Cloud project ID where the BigQuery table resides.
            dataset_id (str): The dataset ID containing the table.
            table_id (str): The table ID with trip data.
            square (Square): An object defining the coordinates of the area's boundaries, with
                `upper_left`, `upper_right`, `bottom_right`, and `bottom_left` properties.

        Returns:
            List[bigquery.Row]: A list of rows where each row represents the count of trips
            for a specific week within the defined area.

        Raises:
            google.cloud.exceptions.GoogleCloudError: If the query fails due to issues with
            BigQuery service.

        Note:
            The SQL query uses spatial functions to identify trips within the area defined
            by the provided `Square` object.
        """
        self.core_table = f"`{project_id}.{dataset_id}.{table_id}`"
        query = f"""
            SELECT
                COUNT(1) AS count_of_trips,
                TIMESTAMP_BUCKET(TIMESTAMP(datetime), INTERVAL 1 WEEK) AS time
            FROM {self.core_table}
            WHERE
                ST_CONTAINS(
                    ST_MAKEPOLYGON(ST_MAKELINE([
                        ST_GEOGFROMTEXT('POINT({square.upper_left})'),
                        ST_GEOGFROMTEXT('POINT({square.upper_right})'),
                        ST_GEOGFROMTEXT('POINT({square.bottom_right})'),
                        ST_GEOGFROMTEXT('POINT({square.bottom_left})')
                    ])),
                    ST_MAKELINE(
                        ST_GEOGFROMTEXT(origin_coord),
                        ST_GEOGFROMTEXT(destination_coord)
                    )
                )
            GROUP BY
                time
            """

        query_job = self.__client.query(query)
        rows = query_job.result()

        return list(rows)
