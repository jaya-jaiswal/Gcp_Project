# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "dataflow.googleapis.com",
    "composer.googleapis.com"
  ])
  service = each.key
}

# GCS Bucket (landing)
resource "google_storage_bucket" "landing" {
  name     = "${var.project_id}-landing-bucket"
  location = var.region
  force_destroy = true
}

# GCS Bucket (dataflow temp)
resource "google_storage_bucket" "temp" {
  name     = "${var.project_id}-temp-bucket"
  location = var.region
  force_destroy = true
}

# BigQuery Dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = "retail_dataset"
  location   = var.region
}

# Composer (light config)
resource "google_composer_environment" "composer" {
  name   = "retail-composer"
  region = var.region

  config {
    node_config {
      machine_type = "e2-medium"
    }
  }
}