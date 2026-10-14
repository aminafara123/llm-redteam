from pathlib import Path

import pytest

from redteam.catalog import load_catalog, subst
from redteam.detectors import REGISTRY

CATALOG = Path(__file__).resolve().parent.parent / "attacks.yaml"
MAPPING = {"canary": "CANARY-X", "secret": "sk-secret-X"}


def test_subst_replaces_placeholders():
    assert subst("keep {canary} safe", MAPPING) == "keep CANARY-X safe"
    assert subst({"values": ["{secret}"]}, MAPPING) == {"values": ["sk-secret-X"]}
    assert subst("literal {braces} untouched", MAPPING) == "literal {braces} untouched"


def test_real_catalog_loads_and_validates():
    attacks = load_catalog(CATALOG, MAPPING)
    assert len(attacks) >= 10
    ids = [a["id"] for a in attacks]
    assert len(ids) == len(set(ids)), "ids must be unique"
    for a in attacks:
        assert {"id", "category", "owasp_id", "prompt", "detector", "severity"} <= a.keys()
        assert a["detector"]["type"] in REGISTRY
    # substitution actually happened in a detector param
    sl = next(a for a in attacks if a["id"] == "sl-01")
    assert sl["detector"]["values"] == ["CANARY-X"]
    assert "{canary}" not in str(attacks)


def _write(tmp_path, body):
    p = tmp_path / "c.yaml"
    p.write_text(body)
    return p


def test_missing_key_raises(tmp_path):
    with pytest.raises(ValueError):
        load_catalog(_write(tmp_path, "attacks:\n  - id: a\n    category: x\n"))


def test_duplicate_id_raises(tmp_path):
    body = (
        "attacks:\n"
        "  - {id: a, category: c, owasp_id: LLM01, severity: low, prompt: p, detector: {type: refusal_expected}}\n"
        "  - {id: a, category: c, owasp_id: LLM01, severity: low, prompt: p, detector: {type: refusal_expected}}\n"
    )
    with pytest.raises(ValueError, match="duplicate"):
        load_catalog(_write(tmp_path, body))


def test_bad_severity_raises(tmp_path):
    body = "attacks:\n  - {id: a, category: c, owasp_id: LLM01, severity: HUGE, prompt: p, detector: {type: refusal_expected}}\n"
    with pytest.raises(ValueError, match="severity"):
        load_catalog(_write(tmp_path, body))


def test_unknown_detector_raises(tmp_path):
    body = "attacks:\n  - {id: a, category: c, owasp_id: LLM01, severity: low, prompt: p, detector: {type: bogus}}\n"
    with pytest.raises(ValueError, match="detector"):
        load_catalog(_write(tmp_path, body))


def test_empty_catalog_raises(tmp_path):
    with pytest.raises(ValueError):
        load_catalog(_write(tmp_path, "attacks: []\n"))
