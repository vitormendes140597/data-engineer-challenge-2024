from typing import Dict, List, Union

from google.cloud import pubsub_v1


class PubSubService:

    def __init__(self, project_id: str, topic_id: str):
        self.__client = pubsub_v1.PublisherClient(
            batch_settings=pubsub_v1.types.BatchSettings(
                max_messages=300,
                max_bytes=51200,  # 50 MB (1024 * 50)
                max_latency=1,  # 1 second
                # Publish when one of the above conditions is met 300 msgs or 50 MB or 1 second
            )
        )
        self._topic_path = self.__client.topic_path(project_id, topic_id)

    def send(self, data: Union[List[Dict[str, str]], Dict[str, str]]) -> None:
        """
        Publishes event data to a Google Cloud Pub/Sub topic.

        This method accepts a single dictionary or a list of dictionaries representing event data,
        encodes each dictionary as a JSON string, and publishes it to the configured Pub/Sub topic.
        The events are published in batches according to the settings defined for the client, with
        a maximum of 300 messages, 50 MB in size, or a 1-second latency.

        Args:
            data (Union[List[Dict[str, str]], Dict[str, str]]): Event data to publish.
                - If a dictionary is provided, it is treated as a single event.
                - If a list of dictionaries is provided, each dictionary represents an individual event.

        Returns:
            None

        Note:
            Uses the Google Cloud Pub/Sub client with pre-configured batch settings.
        """
        import json

        data = [data] if isinstance(data, dict) else data

        for d in data:
            encoded_data = json.dumps(d, default=str).encode("utf-8")
            self.__client.publish(topic=self._topic_path, data=encoded_data)
