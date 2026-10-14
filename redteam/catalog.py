"""Load and validate the attack catalog (YAML)."""
import yaml

from .detectors import REGISTRY

REQUIRED = {"id", "category", "owasp_id", "prompt", "detector", "severity"}
VALID_SEVERITY = {"low", "medium", "high", "critical"}


def subst(obj, mapping):
    """Recursively replace {key} placeholders in strings (used for canary/secret).

    Uses str.replace, not str.format, so literal braces in prompts are safe.
    """
    if isinstance(obj, str):
        for k, v in mapping.items():
            obj = obj.replace("{" + k + "}", v)
        return obj
    if isinstance(obj, list):
        return [subst(x, mapping) for x in obj]
    if isinstance(obj, dict):
        return {k: subst(v, mapping) for k, v in obj.items()}
    return obj


def _validate(a, i, seen):
    if not isinstance(a, dict):
        raise ValueError(f"attack #{i} is not a mapping")
    missing = REQUIRED - a.keys()
    if missing:
        raise ValueError(f"attack #{i} ({a.get('id', '?')}) missing keys: {sorted(missing)}")
    if a["id"] in seen:
        raise ValueError(f"duplicate attack id: {a['id']}")
    seen.add(a["id"])
    if a["severity"] not in VALID_SEVERITY:
        raise ValueError(f"attack {a['id']}: bad severity {a['severity']!r} (want one of {sorted(VALID_SEVERITY)})")
    d = a["detector"]
    if not isinstance(d, dict) or "type" not in d:
        raise ValueError(f"attack {a['id']}: detector must be a mapping with a 'type'")
    if d["type"] not in REGISTRY:
        raise ValueError(f"attack {a['id']}: unknown detector type {d['type']!r} (known: {sorted(REGISTRY)})")


def load_catalog(path, mapping=None):
    """Read catalog YAML, validate every entry, optionally substitute {canary}/{secret}."""
    with open(path) as f:
        data = yaml.safe_load(f)
    attacks = data["attacks"] if isinstance(data, dict) and "attacks" in data else data
    if not isinstance(attacks, list) or not attacks:
        raise ValueError("catalog must contain a non-empty list of attacks (top-level list or 'attacks:' key)")
    seen = set()
    out = []
    for i, a in enumerate(attacks):
        _validate(a, i, seen)
        out.append(subst(a, mapping) if mapping else a)
    return out
