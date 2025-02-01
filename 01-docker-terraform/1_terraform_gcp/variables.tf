variable "credentials" {
  description = "My service account key"
  default     = "secrets/terraform-sa-course-data-engineering-2e97d246cf4a.json"
}

variable "project_id" {
  description = "My GCP Project ID"
  default     = "course-data-engineering"
}

variable "project_location" {
  description = "My GCP Project Location"
  default     = "EU"
}

variable "project_region" {
  description = "My GCP Project Region"
  default     = "europe-west2"
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  default     = "demo_dataset"
}

variable "gcs_bucket_name" {
  description = "My GCS Bucket Name"
  default     = "course-data-engineering-demo-bucket"
}
