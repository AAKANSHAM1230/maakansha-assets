resource "google_compute_global_address" "lb_ip" {
  name = "hr-agent-lb-ip"
}


resource "google_compute_region_network_endpoint_group" "serverless_neg" {
  name = "hr-agent-neg"
  network_endpoint_type = "SERVERLESS"
  region = var.region
  cloud_run {service = google_cloud_run_v2_service.hr_agent.name}
}

resource "google_compute_backend_service" "default" {
  name = "hr-agent-backend"
  protocol  = "HTTP"
  port_name = "http"
  timeout_sec = 30
  backend {group = google_compute_region_network_endpoint_group.serverless_neg.id}
  security_policy = google_compute_security_policy.hr_agent_armor.id
}


resource "google_compute_url_map" "default" {
  name = "hr-agent-url-map"
  default_service = google_compute_backend_service.default.id
}

resource "google_compute_target_http_proxy" "default" {
  name = "hr-agent-http-proxy"
  url_map = google_compute_url_map.default.id
}
resource "google_compute_global_forwarding_rule" "default" {
  name = "hr-agent-lb-forwarding-rule"
  target= google_compute_target_http_proxy.default.id
  port_range = "80"
  ip_address = google_compute_global_address.lb_ip.address
}

output "load_balancer_ip" {
  value = google_compute_global_address.lb_ip.address
}