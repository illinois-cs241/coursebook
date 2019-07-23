#!/usr/bin/env python3

"""
Pandoc filter to change each relative URL to absolute
"""

from panflute import run_filter, Str, Header, Image, Math, Link, RawInline
import sys
import re
import os.path

default_image_alt = 'image'

class NoAltTagException(Exception):
    pass

def replace_suffix(content, suffix_old, suffix_new):
    ret = content
    if content.endswith(suffix_old):
        ret = content[:-len(suffix_old)] + suffix_new
    return ret

def deserialize(x):
    """
    Takes a panflute element x and returns
    a basic stringified version of that element
    """

    if type(x) == Str:
        return x.text
    return ' '

def doc_filter(elem, doc):
    if type(elem) == Image:
        # Get the number of chars for the alt tag
        alt_name = ''.join(map(deserialize, elem._content.list))
        alt_length = len(elem._content)
        # No alt means no compile
        # Accessibility by default
        if alt_length == 0 or alt_name.lower() == default_image_alt:
            raise NoAltTagException(elem.url)

        # Otherwise link to the raw user link instead of relative
        # That way the wiki and the site will have valid links automagically
        new_url = replace_suffix(elem.url, '.eps', '.png')
        if not os.path.isfile(new_url):
            raise ValueError('{} Not found'.format(new_url))
        elem.url = new_url
        return elem


def main(doc=None):
    return run_filter(doc_filter, doc=doc)

if __name__ == "__main__":
    main()
