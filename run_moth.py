
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from router import route_prompt

MODEL = "gemma3:1b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def ask_local_model(prompt):
    """Send a prompt to the local Ollama model."""

    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    request = Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urlopen(request, timeout=180) as response:
        result = json.load(response)

    return result["response"]


def main():
    print("=== PROJECT MOTH ===")
    print("Privacy-Aware AI Model Router\n")

    prompt = input("Enter your prompt: ")

    try:
        decision = route_prompt(prompt)
    except ValueError as error:
        print("Error:", error)
        return

    print("\nSelected route:", decision["model"])
    print("Reason:", decision["reason"])

    if decision["model"] != "local":
        print("\nSimulated cloud route selected.")
        print("No cloud request was made.")
        return

    print("\nGenerating local AI response...\n")

    try:
        answer = ask_local_model(prompt)
        print("Gemma:", answer)

    except HTTPError as error:
        print("Ollama API error:", error.code)
        print("Check that gemma3:1b is installed.")

    except (URLError, TimeoutError):
        print("Could not reach the local Ollama server.")
        print("Make sure Ollama is running.")


if __name__ == "__main__":
    main()
