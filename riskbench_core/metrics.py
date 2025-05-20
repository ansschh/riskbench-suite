"""Prometheus metrics for monitoring RiskBench Suite."""

from prometheus_client import Counter, Histogram, start_http_server

# Run metrics
RUN_COUNTER = Counter('riskbench_runs_total', 'Total runs executed')
RUN_DURATION = Histogram('riskbench_run_duration_seconds', 'Run time per run')
RUN_SUCCESS = Counter('riskbench_run_success_total', 'Total successful runs')
RUN_FAILURE = Counter('riskbench_run_failure_total', 'Total failed runs')

# Risk metrics
RISK_BREACH = Counter('riskbench_risk_breach_total', 'Total risk threshold breaches')
RISK_VALUE = Histogram('riskbench_risk_value', 'Risk metric values')

# Dashboard metrics
API_REQUESTS = Counter('riskbench_api_requests_total', 'Total API requests', ['endpoint'])
API_ERRORS = Counter('riskbench_api_errors_total', 'Total API errors', ['endpoint'])
API_LATENCY = Histogram('riskbench_api_latency_seconds', 'API request latency')

def start_metrics_server(port: int = 8001) -> None:
    """Start the Prometheus metrics server.
    
    Args:
        port: Port to run the server on
    """
    start_http_server(port)
