"""Batch runner: for each attack -> call target -> detect -> collect findings -> score.

`run()` is pure: it takes an already-loaded catalog and a `chat_fn` (the target client),
so it is trivially testable offline with a fake/mock chat function and no network.
"""
import llm

from .detectors import run_detector
from .scoring import score


def _finding(a, status, evidence, response=None, passed=None):
    return {
        "id": a["id"],
        "category": a["category"],
        "owasp_id": a["owasp_id"],
        "severity": a["severity"],
        "detector": a["detector"]["type"],
        "prompt": a["prompt"],
        "response": response[:800] if isinstance(response, str) else response,
        "status": status,
        "passed": passed,
        "evidence": evidence,
    }


def run(attacks, system_prompt, chat_fn, model=None, limit=None):
    """Fire every attack at the target via chat_fn; return {findings, summary}.

    chat_fn(messages, model=None) -> str. If it raises llm.LLMError the attack is
    recorded as an 'error' (not a pass), so an unreachable target cannot look safe.
    """
    items = attacks[:limit] if limit else attacks
    findings = []
    # ponytail: sequential one-request-at-a-time; add a ThreadPoolExecutor if a large
    # catalog against a slow endpoint makes wall-clock time matter.
    for a in items:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": a["prompt"]},
        ]
        try:
            resp = chat_fn(messages, model=model)
        except llm.LLMError as e:
            findings.append(_finding(a, "error", f"target unreachable: {e}"))
            continue
        passed, evidence = run_detector(a["detector"], resp)
        findings.append(
            _finding(a, "pass" if passed else "fail", evidence, response=resp, passed=passed)
        )
    return {"findings": findings, "summary": score(findings)}
