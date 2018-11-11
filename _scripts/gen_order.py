"""
This file generates another file
"""
import argparse
import yaml

help_text = """
Converts a order.yaml file into a order.tex files that has a series of includes in the specified order.
The output file is stdout, meaning you should use redirection to save it to a particular file name.
"""

def main(args):
    file_name = args.name
    # Yaml load will load lists in order by default
    reorder = yaml.load(open(file_name, 'r'))
    templ = '\include{{{}}}'

    for file in reorder:
        render = templ.format(file)
        print(render)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(help=help_text)
    parser.add_argument('name', help="Name of the order file", type=str)
    args = parser.parse_args()
    main(args)
