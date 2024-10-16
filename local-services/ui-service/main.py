import os

from fastapi import FastAPI
from gcp import BigQueryService
from models import Square
from typing import Any, List, Dict

PROJECT_ID = os.environ["PROJECT_ID"]
DATASET_ID = os.environ["DATASET_ID"]
TABLE_ID = os.environ["TABLE_ID"]

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/avg_trip_by_area")
def avg_by_area(square: Square) -> List[Dict[str,Any]]:
    """
    Endpoint to retrieve the weekly average count of trips within a specified geographic area.

    This endpoint accepts a `Square` object defining a geographic area, and it returns
    the weekly count of trips that occur within this area. The method uses the BigQueryService
    to query a BigQuery table for the relevant data.

    Args:
        square (Square): An object defining the coordinates of the area's boundaries, with
            `upper_left`, `upper_right`, `bottom_right`, and `bottom_left` properties.

    Returns:
        List[Dict[str,Any]]: A list of rows where each row includes the count of trips
        for each week within the specified area.

    Raises:
        HTTPException: If any error occurs during the BigQuery query execution.

    Note:
        - This method relies on a BigQuery table with trip data specified by constants
            PROJECT_ID, DATASET_ID, and TABLE_ID.
    """
    bq = BigQueryService()

    result = bq.get_average_trips_by_area(
        project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, square=square
    )

    return result
