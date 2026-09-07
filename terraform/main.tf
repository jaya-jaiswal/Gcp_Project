############################################
# Enable Required APIs (safe subset)
############################################

data "google_project" "project" {
  project_id = var.project_id
}

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

############################################
# GCS Bucket (Landing)
############################################
resource "google_storage_bucket" "landing" {
  name     = "${var.project_id}-landing-bucket"
  location = var.region

  uniform_bucket_level_access = true
  force_destroy               = true
}

############################################
# GCS Bucket (Temp)
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
# Composer Service Account
############################################
resource "google_service_account" "composer_sa" {
  account_id   = "composer-sa"
  display_name = "Composer Service Account"
}

############################################
# IAM Roles for Composer
############################################
resource "google_project_iam_member" "composer_roles" {
  for_each = toset([
    "roles/composer.worker",
    "roles/storage.admin",
    "roles/bigquery.admin",
    "roles/dataflow.admin"
  ])

  project = var.project_id   # ✅ ADD THIS

  role   = each.key
  member = "serviceAccount:${google_service_account.composer_sa.email}"
}

############################################
# Cloud Composer Environment
############################################
resource "google_composer_environment" "composer" {
  name   = "retail-composer"
  region = var.region

  config {
    environment_size = "ENVIRONMENT_SIZE_SMALL"

    node_config {
      service_account = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"
    }

    software_config {
      image_version = "composer-2-airflow-2.6.3"
    }
  }
}