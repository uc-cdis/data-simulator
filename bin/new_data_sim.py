import os
import traceback
import sys
import argparse
import json

from datasimulator.new.new_graph import LinkGraph
from dictionaryutils import DataDictionary, dictionary
from datasimulator.new.simulator import simulate_tree


def init_dictionary(url):
    d = DataDictionary(url=url)
    dictionary.init(d)
    # the gdcdatamodel expects dictionary initiated on load, so this can't be
    # imported on module level
    from gdcdatamodel import models as md
    return d, md


def parse_arguments():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(title="action", dest="action")

    simulate_data_cmd = subparsers.add_parser("simulate")
    simulate_data_cmd.add_argument("--url", required=False, help="s3 dictionary link.", nargs='?', default=None)
    simulate_data_cmd.add_argument(
        "--file", required=True, help="file defines the ", nargs='?'
    )
    simulate_data_cmd.add_argument(
        "--path", required=True, help="path to save files to", nargs='?'
    )
    simulate_data_cmd.add_argument(
        "--program", required=False, help="program to generate data", nargs='?'
    )
    simulate_data_cmd.add_argument(
        "--project", required=False, help="project to generate data", nargs='?'
    )

    return parser.parse_args()


def simulate_data(url, program, project, file_path, outpath):
    try:
        d, md = init_dictionary(url)
        with open(file_path, 'r') as config_file:
            numbers = json.load(config_file)
            l_graph = LinkGraph(numbers, d)
        if l_graph:
            simulate_tree(md, program, project, l_graph, outpath)
        else:
            print('Error graph is not created')
    except Exception as ex:
        print(ex)
        print(traceback.print_exc(file=sys.stdout))


def main():
    args = parse_arguments()
    if args.action == 'simulate':
        simulate_data(args.url, args.program, args.project, args.file, args.path)


if __name__ == '__main__':
    main()
