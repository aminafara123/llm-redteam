"""Render results as a markdown report and a machine-readable JSON file."""
import json

HONESTY = (
    "> **Automated red-team test aid, NOT a safety certification.**\n"
    "> These results come from deterministic keyword/regex detectors. Detectors are\n"
    "> heuristics: they produce false passes and false fails. A qualified human MUST\n"
    "> review every finding. A high pass rate does not mean the target model is safe,\n"
    "> compliant, or certified."
)

_STATUS_ICON = {"pass": "PASS", "fail": "FAIL", "error": "ERR "}


def _esc(text):
    """Keep a cell on one line and pipe-safe for a markdown table."""
    return (text or "").replace("\n", " ").replace("|", "\\|").strip()


def to_json(result, meta):
    return json.dumps(
        {"meta": meta, "summary": result["summary"], "findings": result["findings"]},
        indent=2,
    )


def to_markdown(result, meta):
    s = result["summary"]
    findings = result["findings"]
    L = []
    L.append("# LLM Red-Team Report")
    L.append("")
    L.append(HONESTY)
    L.append("")
    L.append("## Run")
    L.append(f"- Tool: `{meta.get('tool', 'llm-redteam')}`")
    L.append(f"- Target: {meta.get('target', 'n/a')}")
    L.append(f"- Catalog: `{meta.get('catalog', 'n/a')}`")
    L.append(f"- Generated: {meta.get('generated_at', 'n/a')}")
    L.append("")
    L.append("## Summary")
    risk = s["risk_score"]
    L.append(f"- **Overall risk score: {risk if risk is not None else 'unknown'} / 100 "
             f"({s['risk_band']})** — higher = more attacks succeeded (severity-weighted)")
    L.append(f"- Attacks: {s['total_attacks']} | tested: {s['tested']} | "
             f"passed: {s['passed']} | failed: {s['failed']} | errors: {s['errors']}")
    pr = s["pass_rate"]
    L.append(f"- Pass rate (resistance): {round(pr * 100, 1) if pr is not None else 'n/a'}%")
    L.append("")
    L.append("## By category")
    L.append("| Category | Passed | Failed | Errors | Pass rate |")
    L.append("|---|---|---|---|---|")
    for cat, c in s["by_category"].items():
        pr = c["pass_rate"]
        L.append(f"| {cat} | {c['passed']} | {c['failed']} | {c['errors']} | "
                 f"{round(pr * 100, 1) if pr is not None else 'n/a'}% |")
    L.append("")
    L.append("## Findings")
    L.append("| Result | ID | Category | OWASP | Severity | Detector | Evidence |")
    L.append("|---|---|---|---|---|---|---|")
    for f in findings:
        L.append(f"| {_STATUS_ICON.get(f['status'], f['status'])} | {f['id']} | {f['category']} "
                 f"| {f['owasp_id']} | {f['severity']} | {f['detector']} | {_esc(f['evidence'])} |")
    L.append("")

    bad = [f for f in findings if f["status"] in ("fail", "error")]
    if bad:
        L.append("## Failed & errored findings (detail)")
        for f in bad:
            L.append(f"### {_STATUS_ICON.get(f['status'], f['status']).strip()} — {f['id']} "
                     f"({f['category']} / {f['owasp_id']}, severity: {f['severity']})")
            L.append(f"- **Detector:** `{f['detector']}` — {f['evidence']}")
            L.append(f"- **Attack prompt:** {_esc(f['prompt'])}")
            if f.get("response") is not None:
                L.append(f"- **Target response (excerpt):** {_esc(f['response'])}")
            L.append("")
    return "\n".join(L).rstrip() + "\n"
