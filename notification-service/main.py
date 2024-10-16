import base64
import json
import os

import functions_framework
from cloudevents.http import CloudEvent

from gcp import BigQueryService, PubSubService
from utils import JobFinishedFormat, JobInProgressFormat, MessageGenerator, SlackService


@functions_framework.cloud_event
def subscribe(cloud_event: CloudEvent) -> None:

    # Environment & General Variables
    slack_webhook = os.environ["SLACK_WEBHOOK"]
    slack_channel = "ingestion-jobs"
    project_id = "jobsity-challenge-vitor"
    dataset_id = "trips"
    status_bq_table_name = "ingestion_control"
    pubsub_topic_id = "status_topic"

    event = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode())

    bq = BigQueryService(
        project_id=project_id,
        dataset_id=dataset_id,
        status_table_name=status_bq_table_name,
    )

    pubsub = PubSubService(project_id=project_id, topic_id=pubsub_topic_id)

    slack = SlackService(webhook=slack_webhook, channel=slack_channel)

    event["current_count"] = bq.get_count(ingestion_id=event["ingestion_id"])

    msg_format = MessageGenerator.generate(event)

    if isinstance(msg_format, JobFinishedFormat):
        slack.send(msg=msg_format.msg)

    if isinstance(msg_format, JobInProgressFormat):
        pubsub.send(event=event)
