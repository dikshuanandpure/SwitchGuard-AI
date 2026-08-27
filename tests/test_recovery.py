import unittest

from backend.recovery_engine import choose_recovery_action


class TestRecoveryEngine(unittest.TestCase):

    def test_successful_payment(self):

        event = {
            "status": "SUCCESS",
            "error_code": None
        }

        result = choose_recovery_action(event)

        self.assertEqual(
            result["action"],
            "NO_ACTION"
        )


    def test_network_error(self):

        event = {
            "status": "FAILED",
            "error_code": "NETWORK_ERROR"
        }

        result = choose_recovery_action(event)

        self.assertEqual(
            result["action"],
            "RETRY_NOW"
        )


    def test_bank_timeout(self):

        event = {
            "status": "FAILED",
            "error_code": "BANK_TIMEOUT"
        }

        result = choose_recovery_action(event)

        self.assertEqual(
            result["action"],
            "RETRY_LATER"
        )


    def test_insufficient_funds(self):

        event = {
            "status": "FAILED",
            "error_code": "INSUFFICIENT_FUNDS"
        }

        result = choose_recovery_action(event)

        self.assertEqual(
            result["action"],
            "ASK_CUSTOMER_ALTERNATIVE_METHOD"
        )


    def test_high_confidence_outage(self):

        event = {
            "status": "FAILED",
            "error_code": "BANK_TIMEOUT"
        }

        incident = {
            "decision": "HIGH_CONFIDENCE_OUTAGE",
            "confidence": 92
        }

        result = choose_recovery_action(
            event,
            incident
        )

        self.assertEqual(
            result["action"],
            "SWITCH_PAYMENT_ROUTE"
        )


if __name__ == "__main__":

    unittest.main()