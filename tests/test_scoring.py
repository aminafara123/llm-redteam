from redteam.scoring import score


def _f(cat, severity, status):
    return {"category": cat, "severity": severity, "status": status}


def test_all_pass_is_zero_risk():
    s = score([_f("a", "high", "pass"), _f("a", "low", "pass")])
    assert s["risk_score"] == 0.0
    assert s["risk_band"] == "none"
    assert s["pass_rate"] == 1.0


def test_weighted_risk_math():
    # one high (weight 7) fails, one low (weight 1) passes -> 7 / 8 = 87.5
    s = score([_f("a", "high", "fail"), _f("a", "low", "pass")])
    assert s["risk_score"] == 87.5
    assert s["risk_band"] == "critical"
    assert s["tested"] == 2 and s["failed"] == 1


def test_errors_excluded_from_risk():
    s = score([_f("a", "critical", "error"), _f("a", "low", "pass")])
    assert s["errors"] == 1
    assert s["tested"] == 1
    assert s["risk_score"] == 0.0  # the critical error is not counted as a pass or fail


def test_all_errors_risk_unknown():
    s = score([_f("a", "high", "error")])
    assert s["tested"] == 0
    assert s["risk_score"] is None
    assert s["risk_band"] == "unknown"
    assert s["pass_rate"] is None


def test_per_category_breakdown():
    s = score([_f("inj", "high", "fail"), _f("inj", "high", "pass"), _f("leak", "medium", "pass")])
    cats = s["by_category"]
    assert cats["inj"]["pass_rate"] == 0.5
    assert cats["leak"]["passed"] == 1 and cats["leak"]["failed"] == 0
