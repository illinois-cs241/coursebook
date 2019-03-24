#!/usr/bin/env python3

"""
Pandoc filter to grab the different header levels as yaml to stderr
"""

from panflute import run_filter, Str, Header, MetaMap
import sys
import atexit
import yaml
import os
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# Metadata gleaned from the file
meta = dict(
    name="",
    bib_file="",
    subsections=[],
)

# Max header level
max_level = 2

def exit_handler():
    """
    Loads a metadata file in the environment variable
    Opens and reads the file whether or not it exists.
    Then it overwrites the file with the extra metadata
    from the current tex file
    """
    meta_file_name = os.environ['META_FILE_NAME']
    with open(meta_file_name, 'r') as f:
        new_meta = yaml.load(f, Loader=Loader)
    if new_meta is None:
        new_meta = [meta]
    else:
        new_meta += [meta]

    out = yaml.dump(new_meta, Dumper=Dumper)
    with open(meta_file_name, 'w') as f:
        f.write(out)

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
            meta['name'] = name
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
