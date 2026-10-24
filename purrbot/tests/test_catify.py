import pytest

from purrbot.catify import catify

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("hello there!", "hewwo dewe nya~ >w<"),
        ("HELLO", "hewwo nya~"),
        ("nana", "nyanya"),
        ("where??", "whewe nyaaaa?"),
        ("42", "42 nya~"),
    ],
)
def test_catify_pinned_outputs(text, expected):
    assert catify(text) == expected


def test_catify_keeps_existing_cat_noise():
    assert catify("meow") == "meow"
    assert catify("nyan") == "nyan"

def test_catify_mangles_purr_before_it_can_count_as_cat_noise():
    assert catify("purr") == "puww nya~"