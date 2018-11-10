#!/usr/bin/env python3
import argparse

import glob
import os
import yaml
import argparse
from jinja2 import Template
import tempfile

filter_template = "_scripts/pandoc_header_filter.py"

class ConvertableTexFile(object):

    def __init__(self, bare_name, tex_name, meta, outdir):
        self.tex_path = tex_name
        self.meta = meta
        self.bare_name = bare_name
        self.bare_title = self.bare_name.title()
        self.md_name = self.bare_title + '.md'
        self.md_path = outdir + '/' + self.md_name


jinja_templ = """
# Home

**NOTE: Do _not_ edit this. This is automatically updated from the tex source. If you see a typo please make a change or a github issue in the main repo, thanks!**

Welcome to Angrave's crowd-sourced System Programming wiki-book!
This wiki is being built by students and faculty from the University of Illinois and is a crowd-source authoring experiment by Lawrence Angrave from CS @ Illinois.

This book is an introduction to programming in C, and system programming (processes, threads, synchronization, networking and more!). We assume you've already had some programming experience, in an earlier computer science course.

{% for chapter in chapters %}
## {{loop.index}}. [{{chapter.meta['name']}}](./{{chapter.bare_title}}){% for section_name in (chapter.meta['subsections'] or []) %}
* [{{section_name}}](./{{chapter.bare_title}}#{{section_name.lower().replace(' ', '-')}}){% endfor %}
{% endfor %}
"""

def gen_home_page(meta_file_name, out_file):
    tmpl = Template(jinja_templ)
    rendered = tmpl.render(chapters=meta_file_name)
    print("Making Home.md")
    with open(out_file, "w") as f:
        f.write(rendered)

def aggregate_meta_data(file_name, metadata_file):
    command_templ = "pandoc --filter={} -s {} > /dev/null 2>> {}"
    command = command_templ.format(filter_template, file_name, metadata_file)
    ret_value = os.system(command)
    if ret_value != 0:
        raise OSError("'{}' Failed".format(command))

def generate_tex_meta(order, outdir, meta_file_name):
    out_tex_names = [path + ".tex" for path in order]
    print("Generating Metadata at {}".format(meta_file_name))

    for tex_name in out_tex_names:
        print("Adding {}".format(tex_name))
        os.system('pandoc --filter=_scripts/pandoc_header_filter.py -s {} > /dev/null 2>>{}'.format(tex_name, meta_file_name))

    os.system('cat {}'.format(meta_file_name))
    metadata = yaml.load(open(meta_file_name, 'r'))

    ret = []

    for i in range(len(order)):
        bare_name = os.path.basename(order[i])
        tex_name = out_tex_names[i]
        meta = metadata[i]
        to_append = ConvertableTexFile(bare_name, tex_name, meta, outdir)
        ret.append(to_append)
    return ret

def main(args):
    order_file = args.order_file
    outdir = args.outdir

    out_file = outdir + '/Home.md'

    order = yaml.load(open(order_file, 'r'))
    tmp_dir = '/tmp'
    (fd, meta_file_name) = tempfile.mkstemp(dir=tmp_dir)
    os.close(fd)

    print("Creating directory")
    files_meta = generate_tex_meta(order, outdir, meta_file_name)

    # 1. Convert files in the order
    print("Converting files to markdown")
    for files_m in files_meta:
        tex_path = files_m.tex_path
        md_path = files_m.md_path
        command = 'pandoc -s {} -o {}'.format(tex_path, md_path)
        print(command)
        os.system(command)

    # 3. Generate Home Page
    gen_home_page(files_meta, out_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('order_file')
    parser.add_argument('outdir')
    args = parser.parse_args()
    main(args)
