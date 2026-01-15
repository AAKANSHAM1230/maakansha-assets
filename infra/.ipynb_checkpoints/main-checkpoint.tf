provider "google" {
  project = var.project_id
  region = var.region
}

resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "firestore.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com"
  ])
  service = each.key
  disable_on_destroy = false
}

resource "google_storage_bucket" "artifacts" {
  name = "${var.project_id}-hr-artifacts"
  location = "US"
  force_destroy = true
  
  uniform_bucket_level_access = true
}

resource "google_cloud_run_v2_service" "hr_agent" {
  name = "hr-agent-repeatble"
  location = var.region
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "gcr.io/${var.project_id}/hr-agent:latest"
      
      env {
        name  = "BUCKET_NAME"
        value = google_storage_bucket.artifacts.name
      }
      env {
        name = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
    }
    service_account = var.service_account_email
  }
}
