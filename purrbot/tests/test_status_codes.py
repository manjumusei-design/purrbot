from purrbot import content, images


def test_every_supported_code_has_a_phrase():
    for code in content.STATUS_CODES:
        assert isinstance(images.status_code_phrase(code), str)


def test_stdlib_phrase():
    assert images.status_code_phrase(404) == "Not found"


def test_own_phrase():
    assert images.status_code_phrase(419) == "Page expired"


def test_no_duplicate_codes():
    assert len(content.STATUS_CODES) == len(set(content.STATUS_CODES))