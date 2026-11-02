"""Regression checks for the correlation gate's accept/reject behavior."""

import unittest

from verify_evidence import validate_correlation


TRACE_A = "1" * 32
TRACE_B = "2" * 32
SPAN_A = "a" * 16
SPAN_B = "b" * 16


class CorrelationGateTests(unittest.TestCase):
    def test_valid_context_pairs_pass(self):
        spans = [{"traceId": TRACE_A, "spanId": SPAN_A},
                 {"traceId": TRACE_A, "spanId": SPAN_B}]
        self.assertEqual(validate_correlation(spans, spans), (TRACE_A, 2))

    def test_unknown_span_in_known_trace_fails(self):
        spans = [{"traceId": TRACE_A, "spanId": SPAN_A}]
        with self.assertRaisesRegex(AssertionError, "Unmatched log"):
            validate_correlation(spans, [{"traceId": TRACE_A, "spanId": SPAN_B}])

    def test_span_from_another_trace_fails(self):
        # Both IDs exist separately, but their combination does not exist.
        spans = [{"traceId": TRACE_A, "spanId": SPAN_A},
                 {"traceId": TRACE_B, "spanId": SPAN_B}]
        with self.assertRaisesRegex(AssertionError, "Unmatched log"):
            validate_correlation(spans, [{"traceId": TRACE_A, "spanId": SPAN_B}])

    def test_zero_span_context_fails(self):
        spans = [{"traceId": TRACE_A, "spanId": SPAN_A}]
        with self.assertRaisesRegex(ValueError, "nonzero"):
            validate_correlation(spans, [{"traceId": TRACE_A, "spanId": "0" * 16}])


if __name__ == "__main__":
    unittest.main()

