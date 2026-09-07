# Enable required APIs
resource "google_storage_bucket" "landing" {
  name     = "${var.project_id}-landing-bucket"
  location = var.region

  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_storage_bucket" "temp" {
  name     = "${var.project_id}-temp-bucket"
  location = var.region

  uniform_bucket_level_access = true
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
    environment_size = "ENVIRONMENT_SIZE_SMALL"
  }
}