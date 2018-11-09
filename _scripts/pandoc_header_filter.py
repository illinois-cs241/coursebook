#!/usr/bin/env python3

"""
Pandoc filter to grab the different header levels as yaml to stderr
"""

from panflute import run_filter, Str, Header
import sys

max_level = 2
def deserialize(x):
    if type(x) == Str:
        return x.text
    return ' '

def output_yaml(elem, doc):
    if type(elem) == Header and elem.level <= max_level:
        name = ''.join(map(deserialize, elem.content.list))
        name = '"{}"'.format(name)
        spacing = '  ' * (elem.level)
        if elem.level == max_level:
            out = "{}- {}".format(spacing, name)
        elif elem.level == 1:
            out = "-\n{}name: {}\n{}subsections:".format(spacing, name, spacing)
        else:
            out = "{}{}:".format(spacing, name)
        print(out, file=sys.stderr)

    return elem

def main(doc=None):
    return run_filter(output_yaml, doc=doc)

if __name__ == "__main__":
    main()
