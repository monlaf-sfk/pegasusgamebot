from __future__ import annotations

from aiogram.types import InputFile, FSInputFile

photos = {}


def get_photo(a: str):
    if a in photos:
        return photos[a]
    else:
        xa = a + '.jpg' if '.' not in a else a[:-4] + a[-4:]
        set_photo(a, FSInputFile(f'assets/img/{xa}'))
        return photos[a]


def escape(s, quote=True):
    """
    Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true (the default), the quotation mark
    characters, both double quote (") and single quote (') characters are also
    translated.
    """
    s = s.replace("&", "&amp;")  # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
        s = s.replace('\'', "&#x27;")
    return s


def set_photo(a: str, b: str | InputFile):
    global photos
    photos[a] = b
    return b
