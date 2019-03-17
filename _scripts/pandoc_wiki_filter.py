#!/usr/bin/env python3

"""
Pandoc filter to change each relative URL to absolute
"""

from panflute import run_filter, Str, Header, Image, Math, Link, RawInline
import sys
import re

base_raw_url = 'https://raw.githubusercontent.com/illinois-cs241/coursebook/master/'

class NoAltTagException(Exception):
    pass

def change_base_url(elem, doc):
    if type(elem) == Image:
        # Get the number of chars for the alt tag
        alt_length = len(elem._content)

        # No alt means no compile
        # Accessibility by default
        if alt_length == 0:
            raise NoAltTagException(elem.url)

        # Otherwise link to the raw user link instead of relative
        # That way the wiki and the site will have valid links automagically
        elem.url = base_raw_url + elem.url
        return elem

    if isinstance(elem, Math):
        # Fix superscripts and subscripts
        # TODO: Fix regexes and return new raw HTML element in the math instead of inline
        elem.text = re.sub(r'_([A-Za-z0-9])\b', r'<sub>\g<1></sub>', elem.text)
        elem.text = re.sub(r'_\{([A-Za-z0-9]+)\}\b', r'<sub>\g<1></sub>', elem.text)
        elem.text = re.sub(r'\^([-_A-Za-z0-9])', r'<sup>\g<1></sup>', elem.text)
        elem.text = re.sub(r'\^{([-_A-Za-z0-9]+)}', r'<sup>\g<1></sup>', elem.text)
        return elem
    if isinstance(elem, Link):
        # Transform all Links into a tags
        # Reason being is github and jekyll are weird
        # About leaving html as is and markdown as parsing
        # So we change everything to avoid ambiguity
        # There is a script injection possibility here so be careful

        url = elem.url
        title = str(elem.title)
        if title == "":
            title = elem.url
        link = '<a href="{}">{}</a>'.format(url, title)
        return RawInline(link)



def main(doc=None):
    return run_filter(change_base_url, doc=doc)

if __name__ == "__main__":
    main()
