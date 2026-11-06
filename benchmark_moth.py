
import csv
import time
from pathlib import Path
from statistics import mean

from router import route_prompt
from run_moth import ask_local_model


# Synthetic prompts: do not use real private information.
PROMPTS = [
    (
        "simple_1",
        "What is artificial intelligence?"
    ),
    (
        "simple_2",
        "Explain Python lists."
    ),
    (
        "simple_3",
        "What is machine learning?"
    ),
    (
        "privacy_1",
        "My fake email is demo@example.com"
    ),
    (
        "complex_1",
        "Explain how distributed systems coordinate "
        "multiple servers while maintaining data "
        "consistency, recovering from unexpected "
        "failures, balancing workloads, and managing "
        "concurrent requests during periods of "
        "extremely high network traffic."
    ),
    (
        "complex_2",
        "Describe how a machine learning pipeline "
        "can process large datasets, handle missing "
        "values, train different models, evaluate "
        "their accuracy, and monitor performance "
        "after deployment across multiple "
        "computing environments."
    ),
]


def run_benchmark():
    results = []

    print("=== PROJECT MOTH BENCHMARK ===\n")

    for prompt_id, prompt in PROMPTS:

        start = time.perf_counter()
        decision = route_prompt(prompt)
        routing_ms = (
            time.perf_counter() - start
        ) * 1000

        selected_model = decision["model"]
        inference_ms = ""
        status = "simulated_only"
        response_chars = ""

        if selected_model == "local":
            print(f"Running local inference: {prompt_id}")

            start = time.perf_counter()

            try:
                response = ask_local_model(prompt)
                inference_ms = round(
                    (time.perf_counter() - start) * 1000,
                    2
                )
                response_chars = len(response)
                status = "success"

            except Exception as error:
                status = (
                    f"error_{type(error).__name__}"
                )
        else:
            print(f"Simulated cloud route: {prompt_id}")

        results.append({
            "prompt_id": prompt_id,
            "route": selected_model,
            "routing_ms": round(routing_ms, 4),
            "inference_ms": inference_ms,
            "response_chars": response_chars,
            "status": status
        })

    # Save results locally.
    output_folder = Path("results")
    output_folder.mkdir(exist_ok=True)

    output_file = output_folder / "benchmark.csv"

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )

        writer.writeheader()
        writer.writerows(results)

    # Print performance summary.
    successful_local_times = [
        row["inference_ms"]
        for row in results
        if row["status"] == "success"
    ]

    print("\n=== BENCHMARK SUMMARY ===")
    print("Prompts tested:", len(results))

    print(
        "Local routes:",
        sum(r["route"] == "local" for r in results)
    )

    print(
        "Simulated cloud routes:",
        sum(
            r["route"] == "simulated_cloud"
            for r in results
        )
    )

    print(
        "Average routing latency (ms):",
        round(mean(
            r["routing_ms"] for r in results
        ), 4)
    )

    if successful_local_times:
        print(
            "Average local inference latency (ms):",
            round(mean(successful_local_times), 2)
        )

    print("\nResults saved to:", output_file)


if __name__ == "__main__":
    run_benchmark()
