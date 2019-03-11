#!/usr/bin/env python3
import argparse

import glob
import os
import yaml
import argparse
import subprocess
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

Welcome to System Programming coursebook!

This coursebook is being built by students and faculty from the University of Illinois. It is based on a crowd-source authoring wikibook experiment by Lawrence Angrave from CS @ Illinois, but is now its own .tex based project. It's source is located at [the github link](https://github.com/illinois-cs241/coursebook) which you can find a pdf version of the book as well.

This book is an introduction to programming in C, and system programming (processes, threads, synchronization, networking and more!). We assume you've already had some programming experience, in an earlier computer science course.

{% for chapter in chapters %}
## {{loop.index}}. [{{chapter.meta['name']}}](./{{chapter.bare_title}}){% for section_name in (chapter.meta['subsections'] or []) %}
{{loop.index}}. [{{section_name}}](./{{chapter.bare_title}}#{{section_name.lower().replace(' ', '-')}}){% endfor %}
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
        os.system('pandoc --filter ./_scripts/pandoc_header_filter.py -s {} > /dev/null 2>>{}'.format(tex_name, meta_file_name))

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
    prelude_file = 'prelude.tex'
    github_shim = 'github_redefinitions.tex'
    # 1. Convert files in the order
    print("Converting files to markdown")
    sed_regex = r'0,/\\\[1\\\]\\\[\\\]/{//d;}'
    for files_m in files_meta:
        tex_path = files_m.tex_path
        (fd, tex_tmp_path) = tempfile.mkstemp(dir=tmp_dir)
        os.close(fd)
        os.system('cat {} {} {} > {}'.format(prelude_file,
                                             github_shim,
                                             tex_path, tex_tmp_path))
        md_path = files_m.md_path
        command = 'pandoc --toc --self-contained -f latex -t markdown_github -s --filter _scripts/pandoc_wiki_filter.py {} -o {} '.format(tex_tmp_path, md_path)
        print(command)
        os.system(command)
        subprocess.check_call(['sed', '-i', sed_regex, md_path])

    # 3. Generate Home Page
    gen_home_page(files_meta, out_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('order_file')
    parser.add_argument('outdir')
    args = parser.parse_args()
    main(args)
