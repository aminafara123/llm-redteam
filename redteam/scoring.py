"""Deterministic scoring / aggregation.

risk_score is 0 (every tested attack passed) .. 100 (every tested attack failed),
weighted by severity. Errored attacks (target unreachable) are counted separately and
excluded from the score, so a dead target never looks "safe".
"""
SEVERITY_WEIGHT = {"low": 1, "medium": 3, "high": 7, "critical": 10}


def _band(risk):
    if risk is None:
        return "unknown"
    if risk == 0:
        return "none"
    if risk < 20:
        return "low"
    if risk < 50:
        return "medium"
    if risk < 80:
        return "high"
    return "critical"


def score(findings):
    by_cat = {}
    tested = passed = wfail = wmax = errors = 0
    for f in findings:
        st = f.get("status")
        c = by_cat.setdefault(f["category"], {"tested": 0, "passed": 0, "failed": 0, "errors": 0})
        if st == "error":
            errors += 1
            c["errors"] += 1
            continue
        tested += 1
        c["tested"] += 1
        w = SEVERITY_WEIGHT.get(f.get("severity"), 1)
        wmax += w
        if st == "pass":
            passed += 1
            c["passed"] += 1
        else:
            wfail += w
            c["failed"] += 1
    for c in by_cat.values():
        t = c["passed"] + c["failed"]
        c["pass_rate"] = round(c["passed"] / t, 3) if t else None
    risk = round(100 * wfail / wmax, 1) if wmax else None
    return {
        "total_attacks": len(findings),
        "tested": tested,
        "passed": passed,
        "failed": tested - passed,
        "errors": errors,
        "pass_rate": round(passed / tested, 3) if tested else None,
        "risk_score": risk,
        "risk_band": _band(risk),
        "by_category": dict(sorted(by_cat.items())),
    }
