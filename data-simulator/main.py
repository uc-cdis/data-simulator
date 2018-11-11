import argparse

from dictionaryutils import DataDictionary, dictionary

from graph import Graph


def initialize_dictionary(url):
    dictionary.init(DataDictionary(url=url))


def str2bool(v):
    if v.lower() == "true":
        return True
    elif v.lower() == "false":
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="action", dest="action")

    simulate_data_cmd = subparsers.add_parser("simulate")

    simulate_data_cmd.add_argument("--url", required=True, help="s3 dictionary link.")
    simulate_data_cmd.add_argument(
        "--path", required=True, help="path to save files to"
    )

    simulate_data_cmd.add_argument("--program", required=True)
    simulate_data_cmd.add_argument("--project", required=True)

    simulate_data_cmd.add_argument(
        "--max_samples", required=False, help="max number of samples for each node"
    )

    simulate_data_cmd.add_argument(
        "--random",
        help="randomly generate data numbers for nodes",
        default='False',
    )

    simulate_data_cmd.add_argument(
        "--required_only",
        help="generate only required fields",
        default='False',
    )

    simulate_data_cmd.add_argument(
        "--skip",
        help="skip raising an exception if get error",
        default='True',
    )

    return parser.parse_args()


# url = 'https://s3.amazonaws.com/dictionary-artifacts/datadictionary/develop/schema.json'
# url = 'https://s3.amazonaws.com/dictionary-artifacts/bhcdictionary/0.4.3/schema.json'
# url = 'https://s3.amazonaws.com/dictionary-artifacts/genomel-dictionary/master/schema.json'
# url = 'https://s3.amazonaws.com/dictionary-artifacts/kf-dictionary/kf-v0.1.2/schema.json'
# url = 'https://s3.amazonaws.com/dictionary-artifacts/datadictionary/develop/schema.json'
# url = 'https://s3.amazonaws.com/dictionary-artifacts/ndhdictionary/3.1.21/schema.json'

# python main.py simulate --url https://s3.amazonaws.com/dictionary-artifacts/bhcdictionary/0.4.3/schema.json --path ./data-simulator/sample_test_data --program DEV --project test
def main():
    args = parse_arguments()

    print("Data simulator initialization ...")
    initialize_dictionary(args.url)

    if args.action == "simulate":
        graph = Graph(dictionary, args.program, args.project)
        graph.generate_nodes_from_dictionary()
        graph.construct_graph_edges()
        
        is_skip = str2bool(args.skip)
        is_random = str2bool(args.random)
        required_only = str2bool(args.required_only)
        max_samples = int(args.max_samples) or 1
        path = args.path

        graph.graph_validation(skip=is_skip)

        graph.simulate_graph_data(
            path=path,
            n_samples=max_samples,
            random=is_random,
            required_only=required_only,
            skip=is_skip,
        )


if __name__ == "__main__":
    main()
