import unittest
from unittest.mock import Mock, patch

from healthtech_metrics import report_appointment_flow
from metrics_client import InfraiMetrics


class AppointmentMetricsTest(unittest.TestCase):
    @patch("healthtech_metrics.InfraiMetrics")
    def test_flow_reports_counter_and_gauge(self, metrics_type: Mock) -> None:
        metrics = metrics_type.return_value

        report_appointment_flow(metrics, status="confirmed", channel="web")

        self.assertEqual(metrics.report.call_count, 2)
        metrics.report.assert_any_call(
            "appointments.created", 1, "counter", {"status": "confirmed", "channel": "web"}
        )
        metrics.report.assert_any_call(
            "appointments.queue_depth", 0, "gauge", {"channel": "web"}
        )


class InfraiMetricsTest(unittest.TestCase):
    @patch("metrics_client.requests.request")
    @patch("metrics_client.uuid.uuid4", return_value="test-idempotency-key")
    def test_report_sends_contract_fields(
        self, uuid_type: Mock, request: Mock
    ) -> None:
        request.return_value.json.return_value = {"ok": True, "data": {}}
        metrics = InfraiMetrics(api_key="test-key")

        metrics.report("appointments.created", 1, "counter", {"status": "confirmed"})

        payload = request.call_args.kwargs["json"]
        self.assertEqual(payload["idempotency_key"], "test-idempotency-key")
        self.assertEqual(set(payload), {"name", "value", "type", "tags", "idempotency_key"})


if __name__ == "__main__":
    unittest.main()
