resource "google_cloudfunctions2_function" "notification-service" {
  project  = var.project_name
  name     = "notification-service"
  location = var.location

  build_config {
    runtime     = "python312"
    entry_point = "subscribe"
    source {
      storage_source {
        bucket = "notification-service-bucket-jobsity"
        object = "code/service.zip"
      }
    }
  }

  service_config {
    max_instance_count             = 1
    min_instance_count             = 1
    timeout_seconds                = 120
    all_traffic_on_latest_revision = true
    environment_variables = {
      SLACK_WEBHOOK = var.slack_webhook
    }
    service_account_email = jsondecode(file("./credentials.json"))["client_email"]
  }

  event_trigger {
    trigger_region = var.location
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.status-topic.id

  }
}