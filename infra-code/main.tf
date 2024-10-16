resource "google_bigquery_dataset" "events-dataset" {
  dataset_id = "trips"
  location   = var.location
}

resource "google_bigquery_table" "trips" {
  dataset_id = google_bigquery_dataset.events-dataset.dataset_id
  table_id   = "trips"

  schema              = file("./assets/trips_schema.json")
  deletion_protection = false

  clustering = [
    "origin_coord",
    "destination_coord",
    "datetime"
  ]

}

resource "google_bigquery_table" "ingestion-control" {
  dataset_id = google_bigquery_dataset.events-dataset.dataset_id
  table_id   = "ingestion_control"
  view {
    query = templatefile("./assets/ingestion_control.sql", {
      project_id = google_bigquery_dataset.events-dataset.project
      dataset_id = google_bigquery_table.trips.dataset_id
      table_id   = google_bigquery_table.trips.table_id
    })
    use_legacy_sql = false
  }
  deletion_protection = false
}

resource "google_pubsub_topic" "events-topic" {
  name = "events_topic"
}

resource "google_pubsub_topic" "status-topic" {
  name = "status_topic"
}

resource "google_pubsub_subscription" "bq-subscription" {
  name  = "bigquery-subscription"
  topic = google_pubsub_topic.events-topic.id

  bigquery_config {
    table            = "${google_bigquery_table.trips.project}.${google_bigquery_table.trips.dataset_id}.${google_bigquery_table.trips.table_id}"
    use_table_schema = true
  }

}


