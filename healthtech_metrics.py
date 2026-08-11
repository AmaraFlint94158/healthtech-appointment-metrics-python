"""Report the business signals from a small healthtech appointment service."""

from metrics_client import InfraiMetrics


def report_appointment_flow(metrics: InfraiMetrics, status: str, channel: str) -> None:
    """Send a counter for the flow and a gauge for the current queue depth."""
    common_tags = {"status": status, "channel": channel}
    metrics.report("appointments.created", 1, "counter", common_tags)
    metrics.report("appointments.queue_depth", 0, "gauge", {"channel": channel})


def main() -> None:
    metrics = InfraiMetrics()
    report_appointment_flow(metrics, status="confirmed", channel="web")
    print("reported appointment counter and queue gauge")


if __name__ == "__main__":
    main()
