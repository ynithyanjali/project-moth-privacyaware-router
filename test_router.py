
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
        result = route_prompt(prompt)
        self.assertEqual(
            result["model"], "simulated_cloud"
        )

    def test_private_email(self):
        result = route_prompt(
            "My email is test@example.com"
        )
        self.assertEqual(
            result["reason"],
            "Potentially sensitive information detected"
        )

    def test_private_identifier(self):
        result = route_prompt(
            "My test SSN is 000-00-0000"
        )
        self.assertEqual(result["model"], "local")

    def test_password_keyword(self):
        result = route_prompt(
            "Help me change my password"
        )
        self.assertEqual(
            result["reason"],
            "Potentially sensitive information detected"
        )

    def test_empty_prompt(self):
        with self.assertRaises(ValueError):
            route_prompt("")

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            route_prompt(None)


if __name__ == "__main__":
    unittest.main()
