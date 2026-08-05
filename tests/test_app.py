"""PhishGuard — end-to-end tests (stdlib unittest, no extra deps)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import app, analyze  # noqa: E402

PHISH_SAMPLE = """Subject: URGENT: Your account has been suspended

Dear Customer,

Due to unusual activity, your account has been temporarily suspended. Please verify your identity at: http://paypa1-secure.com/verify/login

Click here: http://paypa1-secure.com/verify/login !!!

Please provide your password, credit card details and SSN for verification.

Failure to act within 24 hours will result in permanent closure of your account.

From: support@paypal.com | Reply-To: verify@pay-pal-verify.net

Attachment: invoice_99821.zip

Best regards,
Customer Support Team"""

LEGIT_SAMPLE = """Subject: Your order #48217 has shipped

Dear Chiara,

I hope this message finds you well.

Your order #48217 has shipped and is expected to arrive on Monday. You can track it at https://www.amazon.com.

Let me know if you have any questions.

Best regards,
Marco Rossi
TechFlow Ltd
Project Manager"""


class TestModel(unittest.TestCase):
    def test_phishing_high_score(self):
        res = analyze(PHISH_SAMPLE)
        self.assertGreaterEqual(res["score"], 60)
        self.assertIn(res["label"], ("PHISHING", "SUSPICIOUS"))

    def test_legit_low_score(self):
        res = analyze(LEGIT_SAMPLE)
        self.assertLessEqual(res["score"], 45)
        self.assertIn(res["label"], ("SAFE", "SUSPICIOUS"))

    def test_score_bounds(self):
        for sample in (PHISH_SAMPLE, LEGIT_SAMPLE):
            res = analyze(sample)
            self.assertTrue(0 <= res["score"] <= 100)
            self.assertTrue(res["active_features"])
            self.assertIn("score", res)


class TestAPI(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_api_phishing(self):
        r = self.client.post("/api/analyze", json={"text": PHISH_SAMPLE})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertGreaterEqual(data["score"], 60)

    def test_api_missing_text(self):
        r = self.client.post("/api/analyze", json={})
        self.assertEqual(r.status_code, 400)

    def test_index_page(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"PhishGuard", r.data)


if __name__ == "__main__":
    unittest.main()
