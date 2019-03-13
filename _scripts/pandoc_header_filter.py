#!/usr/bin/env python3

"""
Pandoc filter to grab the different header levels as yaml to stderr
"""

from panflute import run_filter, Str, Header
import sys

# Whether or not the chapter has been displayed yet
top_level_displayed = False

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
    global top_level_displayed

    if type(elem) == Header and elem.level <= max_level:
        # Format what the title is going to look like
        name = ''.join(map(deserialize, elem.content.list))
        name = '"{}"'.format(name)

        # Get the right number of spaces -- TODO: Switch to json
        spacing = '  ' * (elem.level)

        if elem.level == max_level:
            # If we didn't display the chapter, give a dummy section so that yaml is still fine
            if not top_level_displayed:
                print("-\n  name: \"[Untitled]\"\n  subsections:", file=sys.stderr)
                top_level_displayed = True

            # Otherwise output the section as a list
            out = "{}- {}".format(spacing, name)
        elif elem.level == 1:
            # If we are displaying a chapter, include a special entry for it
            top_level_displayed = True
            out = "-\n{}name: {}\n{}subsections:".format(spacing, name, spacing)
        else:
            # If we display anything else, then give it to the next level
            out = "{}{}:".format(spacing, name)
        print(out, file=sys.stderr)

    return elem

def main(doc=None):
    return run_filter(output_yaml, doc=doc)

if __name__ == "__main__":
    main()
