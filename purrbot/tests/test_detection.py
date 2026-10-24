import pytest

from purrbot import detection


@pytest.mark.parametrize("text", ["MEOW", "meow!", "(cat)", ":3", "purr purr"])
def test_cat_word_hits(text):
    assert detection.cat_word_in(text)


@pytest.mark.parametrize("text", ["meowing", "category", "merrrrp"])
def test_cat_word_misses(text):
    assert not detection.cat_word_in(text)


@pytest.mark.parametrize("text", ["quack", "duckie", "DUCK!"])
def test_duck_word_hits(text):
    assert detection.duck_word_in(text)


@pytest.mark.parametrize("text", ["ducks", "quacking", "duckling"])
def test_duck_word_misses(text):
    assert not detection.duck_word_in(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("got 418 again", 418),
        ("cat104", None),
        ("999", None),
        ("418! 502", 418),
    ],
)
def test_status_code_in(text, expected):
    assert detection.status_code_in(text) == expected


def test_detectors_stay_pure():
    assert detection.cat_word_in("nothing here") is False
    assert detection.duck_word_in("nothing here") is False
    assert detection.status_code_in("nothing here") is None
