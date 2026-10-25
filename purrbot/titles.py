from purrbot import content

_TITLES = {
    "cat": content.CAT_PICTURE_TITLES,
    "duck": content.DUCK_PICTURE_TITLES,
}


class PictureTitles:
    def __init__(self) -> None:
        self._index: dict[str, int] = {}

    def next(self, kind: str) -> str:
        titles = _TITLES[kind]
        index = (self._index.get(kind, -1) + 1) % len(titles)
        self._index[kind] = index
        return titles[index]