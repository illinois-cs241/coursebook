#!/usr/bin/env python3

"""
Pandoc filter to change each relative URL to absolute
"""

from panflute import run_filter, Str, Header, Image
import sys

base_raw_url = 'https://raw.githubusercontent.com/illinois-cs241/coursebook/master/'

class NoAltTagException(Exception):
    pass

def change_base_url(elem, doc):
    if type(elem) == Image:
        alt_length = len(elem._content)
        if alt_length == 0:
            raise NoAltTagException(elem.url)
        elem.url = base_raw_url + elem.url
        return elem

def main(doc=None):
    return run_filter(change_base_url, doc=doc)

if __name__ == "__main__":
    main()
