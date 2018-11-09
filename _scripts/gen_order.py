import argparse
import yaml

def main(args):
    file_name = args.name
    reorder = yaml.load(open(file_name, 'r'))
    templ = '\include{{{}}}'
    for file in reorder:
        render = templ.format(file)
        print(render)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    args = parser.parse_args()
    main(args)
