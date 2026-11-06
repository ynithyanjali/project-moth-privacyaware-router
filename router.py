
import re


def contains_sensitive_data(prompt):
    """Detect basic patterns that may indicate private data."""
    email = r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"
    ssn = r"\b\d{3}-\d{2}-\d{4}\b"

    sensitive_words = [
        "password",
        "private key",
        "social security",
    ]

    return (
        bool(re.search(email, prompt))
        or bool(re.search(ssn, prompt))
        or any(word in prompt.lower() for word in sensitive_words)
    )


def route_prompt(prompt):
    """Choose a local or simulated cloud route."""

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must be a non-empty string")

    if contains_sensitive_data(prompt):
        return {
            "model": "local",
            "reason": "Potentially sensitive information detected",
        }

    if len(prompt.split()) <= 20:
        return {
            "model": "local",
            "reason": "Short prompt suitable for local processing",
        }

    return {
        "model": "simulated_cloud",
        "reason": "Longer prompt selected for simulated cloud routing",
    }


if __name__ == "__main__":
    examples = [
        "What is machine learning?",
        "My email is student@example.com",
        (
            "Explain how a distributed computer system handles "
            "thousands of simultaneous requests while maintaining "
            "reliability, minimizing latency, and recovering from "
            "unexpected failures across multiple servers."
        ),
    ]

    for prompt in examples:
        result = route_prompt(prompt)
        print(f"Prompt: {prompt}")
        print(f"Route: {result['model']}")
        print(f"Reason: {result['reason']}")
        print()
