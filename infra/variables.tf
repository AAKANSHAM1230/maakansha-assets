variable "project_id" {
  description = "The project ID"
  type        = string
}

variable "region" {
  description = "Region to deploy to"
  type        = string
  default     = "us-central1"
}

variable "service_account_email" {
  description = "Email of the service account"
  type        = string
}