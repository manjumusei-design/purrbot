from purrbot import content
from purrbot.titles import PictureTitles

def test_cat_rotation_cycles_every_title_in_order():
    titles = PictureTitles()
    shown = [titles.next("cat") for _ in content.CAT_PICTURE_TITLES]
    assert shown == content.CAT_PICTURE_TITLES

def test_duck_rotation_never_repeats_in_a_row():
    titles = PictureTitles()
    shown = [titles.next("duck") for _ in range(len(content.DUCK_PICTURE_TITLES) * 3)]
    assert all(previous != current for previous, current in zip(shown, shown[1:], strict=False))
    assert set(shown) == set(content.DUCK_PICTURE_TITLES)


def test_kinds_keep_separate_position():
    titles = PictureTitles()
    assert titles.next("cat") == content.CAT_PICTURE_TITLES[0]
    assert titles.next("duck") == content.DUCK_PICTURE_TITLES[0]
    assert titles.next("cat") == content.CAT_PICTURE_TITLES[1]