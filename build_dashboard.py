"""Build a static Project Moth dashboard from locally measured CSV data.

Run from anywhere with: py build_dashboard.py
No third-party packages required.
"""

import csv
from html import escape
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "results" / "benchmark.csv"
OUTPUT_PATH = ROOT / "index.html"


def number(value):
    """Return a number, or None for a blank CSV field."""
    if value is None or not str(value).strip():
        return None
    return float(value)


def fmt_ms(value, decimals=2):
    return "Not measured" if value is None else f"{value:,.{decimals}f} ms"


def main():
    if not CSV_PATH.exists():
        raise SystemExit(
            "Missing results/benchmark.csv. First run: py benchmark_moth.py"
        )

    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"prompt_id", "route", "routing_ms", "inference_ms", "status"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise SystemExit("benchmark.csv is missing required columns.")
        rows = list(reader)

    if not rows:
        raise SystemExit("benchmark.csv has no benchmark results.")

    local = sum(r["route"] == "local" for r in rows)
    simulated = sum(r["route"] == "simulated_cloud" for r in rows)
    total = len(rows)
    routing_times = [number(r["routing_ms"]) for r in rows]
    routing_times = [t for t in routing_times if t is not None]
    local_successes = [
        r for r in rows
        if r["route"] == "local" and r["status"] == "success"
        and number(r["inference_ms"]) is not None
    ]
    inference_times = [number(r["inference_ms"]) for r in local_successes]
    avg_route = mean(routing_times) if routing_times else None
    avg_inference = mean(inference_times) if inference_times else None

    def metric(label, value, note):
        return (
            '<article class="metric">'
            f'<div class="metric-label">{escape(label)}</div>'
            f'<div class="metric-value">{escape(str(value))}</div>'
            f'<div class="metric-note">{escape(note)}</div>'
            '</article>'
        )

    metrics = "".join([
        metric("PROMPTS TESTED", total, "Synthetic evaluation inputs"),
        metric("LOCAL ROUTES", local, f"{local / total:.0%} of prompts"),
        metric("SIMULATED CLOUD", simulated, "No cloud API was called"),
        metric("AVERAGE ROUTING", fmt_ms(avg_route, 4), "Decision time across valid rows"),
        metric("AVERAGE LOCAL INFERENCE", fmt_ms(avg_inference),
               f"{len(local_successes)} successful local responses"),
    ])

    # A valid CSV from Step 8 contains only the local and simulated routes.
    route_segments = (
        f'<span class="seg local" style="width:{100 * local / total:.3f}%"></span>'
        f'<span class="seg cloud" style="width:{100 * simulated / total:.3f}%"></span>'
    )

    max_inference = max(inference_times, default=0)
    bars = []
    for r in local_successes:
        value = number(r["inference_ms"])
        width = (100 * value / max_inference) if max_inference else 0
        bars.append(
            '<div class="bar-row">'
            f'<span class="bar-label">{escape(r["prompt_id"])}</span>'
            '<div class="bar-track">'
            f'<div class="bar-fill" style="width:{width:.2f}%"></div>'
            '</div>'
            f'<span class="bar-value">{escape(fmt_ms(value))}</span>'
            '</div>'
        )
    inference_chart = "".join(bars) if bars else (
        '<p class="muted">No successful local inference measurements yet.</p>'
    )

    table_rows = []
    for r in rows:
        routing = number(r["routing_ms"])
        inference = number(r["inference_ms"]) if r["status"] == "success" else None
        status = r["status"]
        status_class = "good" if status == "success" else (
            "neutral" if status == "simulated_only" else "bad"
        )
        cells = [
            escape(r["prompt_id"]),
            escape(r["route"].replace("_", " ")),
            escape(fmt_ms(routing, 4)),
            escape(fmt_ms(inference)),
            f'<span class="status {status_class}">{escape(status)}</span>',
        ]
        table_rows.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>Project Moth | AI Routing Benchmarks</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ background: #0a111b; color: #eaf4f1; margin: 0; line-height: 1.5; }}
    .wrap {{ max-width: 1120px; margin: auto; padding: 38px 24px 70px; }}
    .top {{ display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap: 16px; }}
    .brand {{ font-weight: 800; letter-spacing: .13em; color: #67e6bc; font-size: .85rem; }}
    .tag {{ border: 1px solid #2e655b; color: #a7e5d1; padding: 6px 12px; border-radius: 999px; font-size: .8rem; }}
    h1 {{ font-size: clamp(2rem, 5vw, 3.4rem); line-height: 1.12; letter-spacing: -.04em; margin: 36px 0 14px; }}
    h2 {{ font-size: 1.15rem; margin: 0 0 20px; }}
    .sub,.muted {{ color:#9aafbb; }}
    .sub {{ max-width: 720px; margin: 0 0 32px; }}
    .metrics {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(185px,1fr)); gap:12px; }}
    .metric,.panel {{ background: #101f2a; border: 1px solid #24404a; border-radius: 16px; }}
    .metric {{ padding: 22px 18px; }}
    .metric-label {{ font-size:.75rem; font-weight:700; color:#97b4be; letter-spacing:.07em; }}
    .metric-value {{ font-size: clamp(1.4rem,2.5vw,2rem); font-weight:800; margin: 12px 0 3px; overflow-wrap:anywhere; }}
    .metric-note {{ color:#8ea5af; font-size: .8rem; }}
    .sections {{ display:grid; grid-template-columns: 1fr 1.25fr; gap:18px; margin-top:18px; }}
    .panel {{ padding: 25px; margin-top:18px; }}
    .sections .panel {{ margin-top:0; }}
    .stack {{ display:flex; height:23px; border-radius: 8px; overflow:hidden; background:#32404a; margin:24px 0 17px; }}
    .seg.local,.bar-fill {{ background:linear-gradient(90deg,#178767,#4bdbad); }}
    .seg.cloud {{ background:#7185bc; }}
    .legend {{ display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; font-size:.85rem; }}
    .dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:7px; }}
    .dot.local {{ background:#4bdbad; }} .dot.cloud {{ background:#7185bc; }}
    .bar-row {{ display:grid; grid-template-columns: 85px minmax(50px,1fr) 94px; gap: 12px; align-items:center; margin:14px 0; font-size: .81rem; }}
    .bar-label {{ color:#c2d7d8; overflow-wrap:anywhere; }}
    .bar-track {{ height:15px; background:#243641; border-radius:5px; overflow:hidden; }}
    .bar-fill {{ height:100%; border-radius:5px; }}
    .bar-value {{ text-align:right; font-variant-numeric:tabular-nums; }}
    .scroll {{ overflow-x:auto; }}
    table {{ border-collapse:collapse; width:100%; min-width:650px; font-size: .86rem; }}
    th {{ color:#91aeb8; text-align:left; font-weight:700; font-size:.75rem; }}
    th,td {{ border-bottom:1px solid #29404b; padding: 13px 10px; }}
    .status {{ display:inline-block; border-radius:6px; padding:3px 8px; font-size:.76rem; }}
    .status.good {{ background:#163e34; color:#83e8bf; }}
    .status.neutral {{ background:#29354c; color:#bdc9e8; }}
    .status.bad {{ background:#513038; color:#ffc0c5; }}
    .fineprint {{ font-size:.85rem; color:#aabdc4; }}
    footer {{ color:#7f9aa5; margin-top:35px; font-size:.78rem; }}
    @media(max-width:750px) {{ .sections{{grid-template-columns:1fr;}} .wrap{{padding:24px 15px 50px;}} .panel{{padding:18px;}} }}
  </style>
</head>
<body>
  <main class="wrap">
    <header class="top"><div class="brand">PROJECT MOTH / RESEARCH</div><div class="tag">LOCAL-FIRST · EXPERIMENTAL</div></header>
    <h1>AI Routing Performance</h1>
    <p class="sub">An explainable, privacy-aware routing prototype. All figures below are loaded from recorded benchmark CSV data, not generated estimates.</p>
    <section class="metrics" aria-label="Key metrics">{metrics}</section>
    <div class="sections">
      <section class="panel"><h2>Routing distribution</h2>
        <p class="muted">Where the router selected to send each prompt</p>
        <div class="stack" aria-label="Local {local} prompts; simulated cloud {simulated} prompts">{route_segments}</div>
        <div class="legend"><span><i class="dot local"></i>Local: {local} ({local / total:.1%})</span><span><i class="dot cloud"></i>Simulated: {simulated} ({simulated / total:.1%})</span></div>
      </section>
      <section class="panel"><h2>Local inference latency</h2>
        <p class="muted">Measured wall-clock time per successful local response</p>
        {inference_chart}
      </section>
    </div>
    <section class="panel"><h2>Individual benchmark results</h2>
      <div class="scroll"><table><thead><tr><th>Prompt ID</th><th>Route</th><th>Routing time</th><th>Inference time</th><th>Status</th></tr></thead>
      <tbody>{''.join(table_rows)}</tbody></table></div>
    </section>
    <section class="panel fineprint"><h2>Methodology and limitations</h2>
      <p>The router applies basic sensitive-pattern checks and a word-count threshold. It is a learning prototype, not a verified privacy or complexity classifier.</p>
      <p><strong>Measured:</strong> routing decision time for recorded prompts and local Gemma response time for successful local calls. Local inference times include model loading and other overhead.</p>
      <p><strong>Not measured:</strong> cloud inference latency, cloud costs, response correctness, model quality, or production reliability. A simulated-cloud selection never sends the prompt to a cloud service.</p>
      <p>Results reflect one local run on a small synthetic prompt set. No private prompt text is included in this dashboard.</p>
    </section>
    <footer>Project Moth · Local-first AI routing research prototype · Static report generated from results/benchmark.csv</footer>
  </main>
</body>
</html>
"""

    OUTPUT_PATH.write_text(page, encoding="utf-8")
    print(f"Dashboard created: {OUTPUT_PATH}")
    print(f"Prompts: {total} | Local: {local} | Simulated cloud: {simulated}")
    print("Open index.html in a web browser to view the dashboard.")


if __name__ == "__main__":
    main()
