terraform {
  required_version = ">= 1.5.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "capstone-devops" {
  metadata {
    name = var.namespace
    labels = {
      managed-by = "terraform"
      project    = "capstone-devops"
    }
  }
}

resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "capstone-devops-config"
    namespace = kubernetes_namespace.capstone-devops.metadata[0].name
  }
  data = {
    APP_ENV      = "production"
    SERVICE_NAME = "capstone-devops-api"
    LOG_LEVEL    = "INFO"
  }
}

resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "capstone-devops-secrets"
    namespace = kubernetes_namespace.capstone-devops.metadata[0].name
  }
  type = "Opaque"
  data = {
    DATABASE_SECRET_KEY = base64encode(var.db_secret)
  }
}
