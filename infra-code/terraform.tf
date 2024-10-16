terraform {
  required_version = ">= 1.7.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.21.0"
    }
  }

  backend "gcs" {
    bucket = "tf-state-jobsity-challenge"
    prefix = "terraform/state"
  }
}

provider "google" {
  project     = "jobsity-challenge-vitor"
  region      = "us-east1"
  zone        = "us-east1-a"
  credentials = "./credentials.json"
}
