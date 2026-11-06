
import re

# Words that may indicate technical complexity.
COMPLEXITY_TERMS = (
    "analyze", "evaluate", "design", "optimize",
    "architecture", "distributed", "tradeoff",
    "tradeoffs", "scalability",
)


def contains_sensitive_data(prompt):
    """Detect some common privacy patterns."""
    email = r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"
    ssn = r"\b\d{3}-\d{2}-\d{4}\b"

    sensitive_words = (
        "password", "private key", "social security"
    )

    lower = prompt.lower()

    return (
        bool(re.search(email, prompt))
        or bool(re.search(ssn, prompt))
        or any(word in lower for word in sensitive_words)
    )


def route_prompt(prompt):
    """Route a prompt using an explainable score."""

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must be a non-empty string")

    words = len(prompt.split())

    # Find technical terms in the prompt.
    matches = [
        term for term in COMPLEXITY_TERMS
        if re.search(
            r"\b" + re.escape(term) + r"\b",
            prompt.lower()
        )
    ]

    # Longer prompts receive two additional points.
    score = (2 if words > 20 else 0) + len(matches)

    details = {
        "complexity_score": score,
        "signals": matches
    }

    # Privacy checks take priority over complexity.
    if contains_sensitive_data(prompt):
        return {
            "model": "local",
            "reason": "Potentially sensitive information detected",
            **details
        }

    # High-scoring prompts use simulated cloud routing.
    if score >= 2:
        return {
            "model": "simulated_cloud",
            "reason": "Prompt complexity score reached routing threshold",
            **details
        }

    return {
        "model": "local",
        "reason": "Low complexity score suitable for local processing",
        **details
    }


if __name__ == "__main__":
    examples = (
        "What is machine learning?",
        "Design a distributed system",
        "My email is demo@example.com",
    )

    for prompt in examples:
        print(prompt, "=>", route_prompt(prompt))
