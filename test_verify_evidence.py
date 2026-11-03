"""Regression checks for the correlation gate's accept/reject behavior."""

import unittest

from verify_evidence import validate_correlation, validate_hierarchy


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


class HierarchyGateTests(unittest.TestCase):
    def setUp(self):
        self.spans = [
            {"name": "checkout.request", "traceId": TRACE_A, "spanId": SPAN_A},
            {"name": "inventory.reserve", "traceId": TRACE_A, "spanId": SPAN_B,
             "parentSpanId": SPAN_A},
            {"name": "payment.authorize", "traceId": TRACE_A, "spanId": "c" * 16,
             "parentSpanId": SPAN_A},
        ]

    def test_valid_parent_child_links_pass(self):
        self.assertEqual(validate_hierarchy(self.spans), 2)

    def test_wrong_parent_fails(self):
        self.spans[1]["parentSpanId"] = SPAN_B
        with self.assertRaisesRegex(AssertionError, "parent ID"):
            validate_hierarchy(self.spans)

    def test_child_in_another_trace_fails(self):
        self.spans[1]["traceId"] = TRACE_B
        with self.assertRaisesRegex(AssertionError, "another trace"):
            validate_hierarchy(self.spans)


if __name__ == "__main__":
    unittest.main()
