terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.18.1"
    }
  }
}

provider "google" {
  credentials = "secrets/terraform-sa-course-data-engineering-2e97d246cf4a.json"
  project = "course-data-engineering"
  region  = "europe-west2"
  zone    = "europe-west2-a"
}

resource "google_storage_bucket" "demo-bucket" {
  name          = "course-data-engineering-demo-bucket"
  location      = "EU"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}