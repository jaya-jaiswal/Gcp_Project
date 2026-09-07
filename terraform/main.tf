############################################
# Enable Required APIs
############################################
resource "google_project_service" "services" {
  for_each = toset([
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "dataflow.googleapis.com",
    "composer.googleapis.com",
    "compute.googleapis.com",
    "container.googleapis.com"
  ])
  service = each.key
}

############################################
# GCS Bucket (Landing - CSV files)
############################################
resource "google_storage_bucket" "landing" {
  name     = "${var.project_id}-landing-bucket"
  location = var.region

  uniform_bucket_level_access = true
  force_destroy               = true
}

############################################
# GCS Bucket (Temp - Dataflow)
############################################
resource "google_storage_bucket" "temp" {
  name     = "${var.project_id}-temp-bucket"
  location = var.region

  uniform_bucket_level_access = true
  force_destroy               = true
}

############################################
# BigQuery Dataset
############################################
resource "google_bigquery_dataset" "dataset" {
  dataset_id = "retail_dataset"
  location   = var.region
}

############################################
# Cloud Composer Environment (Airflow)
############################################
resource "google_composer_environment" "composer" {
  name   = "retail-composer"
  region = var.region

  config {
    environment_size = "ENVIRONMENT_SIZE_SMALL"
  }
}