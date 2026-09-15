# Observability design

LangSmith records agent traces; OpenTelemetry connects API, worker, MCP and query spans; Prometheus records service metrics; Grafana displays them. Instrument when those services exist.

Every run carries request_id, run_id, thread_id, user_id and tool_call_id. Record agent/model label, latency, input/output tokens, estimated cost, revision count, SQL query IDs and failure reason. Query evidence includes metric IDs/versions, models, SQL hash, result columns, bounded rows, row count, truncation, timestamps, calculation and confidence/limitations.

Logs exclude secrets, raw review text, fine geolocation and full result bodies. Query literals that identify individuals are redacted. Restricted evidence storage and audit retention are 30 and 90 days respectively for the demo deployment; configuration changes require review.

Alerts: worker/job failures, queue age >60 seconds, DB health failure, query timeout rate >5% over 5 minutes, stale required assets and exhausted budgets. Dashboard groups: reliability, data quality, agent accuracy, cost/latency. Trace export outages must not discard completed findings or retry external mutations.

