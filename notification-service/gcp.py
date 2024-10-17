from concurrent import futures
from typing import Dict

from google.cloud import bigquery, pubsub_v1


class BigQueryService:
    """
    Provides methods for interacting with a BigQuery table to retrieve data and verify event counts.
    """

    def __init__(
        self, project_id: str, dataset_id: str, status_table_name: str
    ) -> None:
        """
        Initializes the BigQueryService instance with a specific BigQuery table.

        Args:
            project_id (str): The Google Cloud project ID where the BigQuery table resides.
            dataset_id (str): The dataset ID containing the table.
            status_table_name (str): The name of the table used for querying event counts.
        """
        self.__client = bigquery.Client()
        self.core_table = f"{project_id}.{dataset_id}.{status_table_name}"

    def get_count(self, ingestion_id: str) -> int:
        """
        Retrieves the count of records in the table matching the specified ingestion ID.

        This method queries a view based on trips raw table to check if the count of records with the
        given `ingestion_id` matches the number of events sent by an invoker.

        Args:
            ingestion_id (str): The unique identifier for the ingestion event to query.

        Returns:
            int: The count of records found for the specified ingestion ID. Returns 0 if
            no matching records are found.

        Raises:
            google.cloud.exceptions.GoogleCloudError: If the query fails due to issues
            with the BigQuery service.
        """
        query = (
            f"SELECT * FROM `{self.core_table}`"
            f'WHERE ingestion_id = "{ingestion_id}"'
        )

        query_job = self.__client.query(query, job_config=bigquery.QueryJobConfig(use_query_cache=False))
        rows = query_job.result()

        for row in rows:
            return row.get("count_of_records")

        return 0


class PubSubService:
    """
    Service for publishing events to a Google Cloud Pub/Sub topic.
    """

    def __init__(self, project_id: str, topic_id: str) -> None:
        """
        Initializes the PubSubService with a specified Pub/Sub topic.

        Args:
            project_id (str): The Google Cloud project ID.
            topic_id (str): The Pub/Sub topic ID where events will be published.
        """

        self.__client = pubsub_v1.PublisherClient()
        self._topic_path = self.__client.topic_path(project_id, topic_id)

    def send(self, event: Dict[str, str]) -> None:
        """
        Publishes an event to the configured Pub/Sub topic.

        This method encodes the provided event as JSON and sends it to the specified
        Pub/Sub topic.

        Args:
            event (Dict[str, str]): The event data to be published as a dictionary.

        Raises:
            google.api_core.exceptions.GoogleAPIError: If the publish request fails.
        """
        import json

        self.__client.publish(
            topic=self._topic_path, data=json.dumps(event).encode("utf-8")
        )
