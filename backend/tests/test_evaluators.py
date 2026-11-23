from types import SimpleNamespace as R

from app.evaluators.exact_match import is_match
from app.evaluators.metrics import compute_metrics


def _r(correct, err=None, lat=100.0):
    return R(is_correct=correct, error=err, latency_ms=lat, input_tokens=10, output_tokens=5)


def _metrics(results, model="openai/gpt-oss-20b"):
    return {m["metric_name"]: m for m in compute_metrics(results, model)}


def test_match_ignores_case_whitespace_and_punctuation():
    assert is_match(" Paris. ", "paris")
    assert is_match('"yes"', "yes")


def test_mismatch():
    assert not is_match("Paris, France", "Paris")


def test_unicode_subscripts_match():
    assert is_match("H₂O", "H2O")


def test_provider_error_is_not_counted_as_wrong_answer():
    m = _metrics([_r(True), _r(False), _r(None, err="timeout", lat=None)])
    assert m["correctness_rate"]["value"] == 0.5
    assert m["correctness_rate"]["details"]["scored"] == 2
    assert abs(m["error_rate"]["value"] - 1 / 3) < 1e-9


def test_p95_latency():
    m = _metrics([_r(True, lat=float(i)) for i in range(1, 21)])
    assert m["latency_ms_p95"]["value"] == 19.0


def test_cost_only_for_known_models():
    assert "estimated_cost_usd" in _metrics([_r(True)])
    assert "estimated_cost_usd" not in _metrics([_r(True)], model="unknown-model")


def test_empty_results():
    assert set(_metrics([])) == {"error_rate"}