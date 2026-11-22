output "namespace" {
  value = kubernetes_namespace.capstone-devops.metadata[0].name
}

output "configmap_name" {
  value = kubernetes_config_map.app_config.metadata[0].name
}
