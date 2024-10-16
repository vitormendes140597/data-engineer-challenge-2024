from typing import Dict


class MessageFormat:
    """
    Base class for formatting messages related to ingestion notifications.
    """

    def __init__(self, event: Dict[str, str]) -> None:
        """
        Initializes the MessageFormat with the provided event data.

        Args:
            event (Dict[str, str]): A dictionary containing event information, including
            ingestion ID, expected count, and current count of events.
        """
        self.event = event
        self.msg_dict = {
            "header": "*Ingestion Notification!* \n",
            "ingestion_id": f"*Ingestion ID:* {self.event.get('ingestion_id')} \n",
            "expected_count": f"*Expected Count of Events:* {self.event.get('count')} \n",
            "current_count": f"*Current Count of Events:* {self.event.get('current_count')}",
        }


class JobFinishedFormat(MessageFormat):
    """
    Class for formatting messages when an ingestion job has finished.
    """

    def __init__(self, event: Dict[str, str]) -> None:
        """
        Initializes the JobFinishedFormat with the provided event data and constructs
        the completion message.

        Args:
            event (Dict[str, str]): A dictionary containing event information.
        """

        super().__init__(event=event)
        self.msg_dict["message"] = "*Message:* The ingestion job has finished! \n"
        self.msg = (
            self.msg_dict["header"]
            + self.msg_dict["message"]
            + self.msg_dict["ingestion_id"]
            + self.msg_dict["expected_count"]
            + self.msg_dict["current_count"]
        )


class JobInProgressFormat(MessageFormat):
    """
    Class for formatting messages when an ingestion job is currently in progress.
    """

    def __init__(self, event: Dict[str, str]) -> None:
        """
        Initializes the JobInProgressFormat with the provided event data and constructs
        the in-progress message.

        Args:
            event (Dict[str, str]): A dictionary containing event information.
        """

        super().__init__(event=event)
        self.msg_dict["message"] = "*Message:* The ingestion job is in progress! \n"
        self.msg = (
            self.msg_dict["header"]
            + self.msg_dict["message"]
            + self.msg_dict["ingestion_id"]
            + self.msg_dict["expected_count"]
            + self.msg_dict["current_count"]
        )


class JobFailedFormat(MessageFormat):
    """
    Class for formatting messages when an ingestion job has failed.
    """

    def __init__(self, event: Dict[str, str]) -> None:
        """
        Initializes the JobFailedFormat with the provided event data and constructs
        the failure message.

        Args:
            event (Dict[str, str]): A dictionary containing event information.
        """
        super().__init__(event=event)
        self.msg_dict["message"] = (
            "*Message:* The ingestion job started a long time and hasn't finished yet! Please take a look.! \n"
        )
        self.msg = (
            self.msg_dict["header"]
            + self.msg_dict["message"]
            + self.msg_dict["ingestion_id"]
            + self.msg_dict["expected_count"]
            + self.msg_dict["current_count"]
        )


class MessageGenerator:
    """
    Generator for creating appropriate message formats based on event status.
    """

    def generate(event: Dict[str, str]) -> MessageFormat:
        """
        Generates a message format based on the status of the ingestion job.

        This method determines the message format to use based on whether the
        current count of events matches the expected count.

        Args:
            event (Dict[str, str]): A dictionary containing event information, including
            the expected count and the current count.

        Returns:
            MessageFormat: An instance of JobFinishedFormat, JobInProgressFormat,
            or JobFailedFormat based on the event status.
        """

        # If all events sent by the invoker were successfully written in BigQuery
        if event["count"] == event["current_count"]:
            return JobFinishedFormat(event=event)
        # If ingestion into BigQuery is still in progress.
        elif event["current_count"] < event["count"]:
            return JobInProgressFormat(event=event)


class SlackService:
    """
    Service for sending messages to a Slack channel using a webhook.
    """

    def __init__(self, webhook: str, channel: str) -> None:
        """
        Initializes the SlackService with the provided webhook URL and channel.

        Args:
            webhook (str): The incoming webhook URL for the Slack channel.
            channel (str): The Slack channel to which messages will be sent.
        """

        self.webook = webhook
        self.channel = channel

    def send(self, msg: str) -> None:
        """
        Sends a message to the configured Slack channel.

        This method constructs a JSON payload containing the message and posts it
        to the specified Slack channel using the configured webhook URL.

        Args:
            msg (str): The message to be sent to the Slack channel.

        Raises:
            requests.exceptions.RequestException: If the request to the Slack webhook fails.
        """

        import json

        import requests

        payload = {
            "channel": self.channel,
            "username": "Bot User",
            "text": msg,
            "link_names": "1",
        }

        headers = {"content-type": "application/json"}
        requests.post(
            self.webook, headers=headers, data=json.dumps(payload), timeout=60
        )
