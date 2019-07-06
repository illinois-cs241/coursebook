#!/usr/bin/env python3

"""
Pandoc filter to change each relative URL to absolute
"""

from panflute import run_filter, Str, Header, Image, Math, Link, RawInline
import sys
import re

base_raw_url = 'https://raw.githubusercontent.com/illinois-cs241/coursebook/master/'
eps_ext = '.eps'
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
        elem.url = base_raw_url + new_url
        return elem

    if isinstance(elem, Math):
        # Raw inline mathlinks so jekyll renders them
        content = elem.text
        escaped = "$$ {} $$".format(content)
        return RawInline(escaped)
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
    return run_filter(doc_filter, doc=doc)

if __name__ == "__main__":
    main()
