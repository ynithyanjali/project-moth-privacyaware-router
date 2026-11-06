
import unittest
from router import route_prompt


class TestProjectMoth(unittest.TestCase):

    def test_short_prompt(self):
        result = route_prompt("What is AI?")
        self.assertEqual(result["model"], "local")

    def test_long_prompt(self):
        prompt = (
            "Explain how a distributed system coordinates "
            "requests across multiple independent servers "
            "while maintaining consistency and fault tolerance "
            "during sudden traffic spikes and unreliable "
            "network conditions across different regions."
        )
        self.assertEqual(
            route_prompt(prompt)["model"],
            "simulated_cloud"
        )

    def test_private_email(self):
        self.assertEqual(
            route_prompt("My email is test@example.com")["reason"],
            "Potentially sensitive information detected"
        )

    def test_private_identifier(self):
        result = route_prompt("My test SSN is 000-00-0000")
        self.assertEqual(result["model"], "local")

    def test_password_keyword(self):
        self.assertEqual(
            route_prompt("Help me change my password")["reason"],
            "Potentially sensitive information detected"
        )

    def test_empty_prompt(self):
        with self.assertRaises(ValueError):
            route_prompt("")

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            route_prompt(None)

    def test_short_but_technical_prompt(self):
        result = route_prompt("Design a distributed system")
        self.assertEqual(
            result["model"], "simulated_cloud"
        )

    def test_privacy_takes_priority(self):
        result = route_prompt(
            "Analyze my private key and design a distributed system"
        )
        self.assertEqual(result["model"], "local")

    def test_explainable_score(self):
        result = route_prompt("Design a distributed system")
        self.assertEqual(result["complexity_score"], 2)
        self.assertIn("distributed", result["signals"])

    def test_one_keyword_stays_local(self):
        result = route_prompt("Compare lists")
        self.assertEqual(result["model"], "local")


if __name__ == "__main__":
    unittest.main()
