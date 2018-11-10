#!/usr/bin/env python3

"""
Pandoc filter to grab the different header levels as yaml to stderr
"""

from panflute import run_filter, Str, Header, Image
import sys

base_raw_url = 'https://raw.githubusercontent.com/illinois-cs241/wikibook-project/master/'

extra_css = "max-width: 60%; display: block; margin: 0 auto;"

def output_yaml(elem, doc):
    if type(elem) == Image:
        elem.url = base_raw_url + elem.url
        elem.attributes['style'] = extra_css
        return elem

def main(doc=None):
    return run_filter(output_yaml, doc=doc)

if __name__ == "__main__":
    main()
