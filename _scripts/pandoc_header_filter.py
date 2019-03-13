#!/usr/bin/env python3

"""
Pandoc filter to grab the different header levels as yaml to stderr
"""

from panflute import run_filter, Str, Header, MetaMap
import sys
import atexit
import yaml

meta = dict(
    title="",
    bib_file="",
    subsections=[],
)

def exit_handler():
    print(yaml.dump([meta]), file=sys.stderr)


max_level = 2
def deserialize(x):
    """
    Takes a panflute element x and returns
    a basic stringified version of that element
    """

    if type(x) == Str:
        return x.text
    return ' '

def output_yaml(elem, doc):
    """
    This function performs a walk along a document and outputs to
    stderr a yaml file that has metadata about the name and the
    subsections of the chapter. Elem is a pandoc valid element
    doc is usually going to be None
    """
    if type(elem) == Header and elem.level <= max_level:
        # Format what the title is going to look like
        name = ''.join(map(deserialize, elem.content.list))

        if elem.level == max_level:
            meta['subsections'].append(name)
        elif elem.level == 1:
            # If we are displaying a chapter, include a special entry for it
            meta['title'] = name
        else:
            pass
    if isinstance(elem, MetaMap):
        dictionary_map = elem._content
        if 'bibliography' in dictionary_map:
            bib_file = deserialize(dictionary_map['bibliography'][0].content[0])
            meta['bib_file'] = bib_file

    return elem

def main(doc=None):
    atexit.register(exit_handler)
    return run_filter(output_yaml, doc=doc)

if __name__ == "__main__":
    main()
