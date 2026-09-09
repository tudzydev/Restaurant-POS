import unittest
from payment import CashPayment, CreditCardPayment, QRPayment


class TestPaymentSpecification(unittest.TestCase):
    """Executable specifications for Payment hierarchy (Section 4 & Section 6, Feature 4)."""

    # --- Feature 4: CashPayment ---

    def test_cash_payment_sufficient_funds(self):
        """CashPayment succeeds when receivedAmount >= amount."""
        payment = CashPayment(amount=100.00, receivedAmount=150.00)
        self.assertEqual(payment.amount, 100.00)
        self.assertEqual(payment.receivedAmount, 150.00)
        self.assertTrue(payment.pay())

    def test_cash_payment_exact_amount(self):
        """CashPayment succeeds when receivedAmount == amount."""
        payment = CashPayment(amount=100.00, receivedAmount=100.00)
        self.assertTrue(payment.pay())

    def test_scenario_4_1_insufficient_cash_payment(self):
        """Scenario 4.1: Insufficient cash payment fails."""
        # Given total amount 100.00 and cash received 80.00
        payment = CashPayment(amount=100.00, receivedAmount=80.00)

        # When pay() is called, Then returns False
        self.assertFalse(payment.pay())

    # --- CreditCardPayment ---

    def test_scenario_4_2_valid_credit_card(self):
        """Scenario 4.2: Valid 16-digit credit card succeeds."""
        # Given card number "1234-5678-9012-3456" and amount 100.00
        payment = CreditCardPayment(amount=100.00, cardNumber="1234-5678-9012-3456")

        # When pay() is called, Then returns True
        self.assertTrue(payment.pay())

    def test_credit_card_with_spaces_succeeds(self):
        """CreditCardPayment strips spaces properly."""
        payment = CreditCardPayment(amount=50.00, cardNumber="1234 5678 9012 3456")
        self.assertTrue(payment.pay())

    def test_credit_card_invalid_length(self):
        """Credit card with non-16 digits fails."""
        payment = CreditCardPayment(amount=50.00, cardNumber="123456789012")
        self.assertFalse(payment.pay())

    def test_credit_card_non_digit_characters(self):
        """Credit card with alphabetic characters fails."""
        payment = CreditCardPayment(amount=50.00, cardNumber="1234-5678-9012-ABCD")
        self.assertFalse(payment.pay())

    # --- QRPayment ---

    def test_qr_payment_valid_transaction_id(self):
        """QRPayment succeeds with non-empty transactionId."""
        payment = QRPayment(amount=75.00, transactionId="TXN-20260909-001")
        self.assertEqual(payment.transactionId, "TXN-20260909-001")
        self.assertTrue(payment.pay())

    def test_qr_payment_empty_transaction_id_fails(self):
        """QRPayment fails with empty transactionId."""
        payment = QRPayment(amount=75.00, transactionId="")
        self.assertFalse(payment.pay())

    def test_qr_payment_whitespace_only_transaction_id_fails(self):
        """QRPayment fails with whitespace-only transactionId."""
        payment = QRPayment(amount=75.00, transactionId="   ")
        self.assertFalse(payment.pay())


if __name__ == "__main__":
    unittest.main()
