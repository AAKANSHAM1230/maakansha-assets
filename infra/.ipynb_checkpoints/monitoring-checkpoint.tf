resource "google_monitoring_dashboard" "hr_agent_dashboard" {
  dashboard_json = <<EOF
{
  "displayName": "HR Agent Health",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "Request Count",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" resource.label.\"service_name\"=\"hr-agent-repeatble\"",
                "aggregation": {
                  "perSeriesAligner": "ALIGN_RATE"
                }
              }
            },
            "plotType": "LINE"
          }]
        }
      },
      {
        "title": "Error Rate (Non-200)",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" resource.label.\"service_name\"=\"hr-agent-repeatble\" metric.label.\"response_code_class\"!=\"2xx\"",
                "aggregation": {
                  "perSeriesAligner": "ALIGN_RATE"
                }
              }
            },
            "plotType": "STACKED_BAR"
          }]
        }
      }
    ]
  }
}
EOF
}