import argparse

from dictionaryutils import DataDictionary, dictionary

from graph import Graph


def initialize_dictionary(url):
    dictionary.init(DataDictionary(url=url))


def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="action", dest="action")

    simulate_data_cmd = subparsers.add_parser("simulate")

    simulate_data_cmd.add_argument("--url", required=True)
    simulate_data_cmd.add_argument("--path", required=True)
    simulate_data_cmd.add_argument("--program", required=True)
    simulate_data_cmd.add_argument("--project", required=True)

    simulate_data_cmd.add_argument("--n_samples", required=False)
    simulate_data_cmd.add_argument("--random", required=False)
    simulate_data_cmd.add_argument("--required_only", required=False)
    simulate_data_cmd.add_argument("--skip", required=False)

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

    # import pdb; pdb.set_trace()
    if args.action == "simulate":
        graph = Graph(dictionary, args.program, args.project)
        graph.generate_nodes_from_dictionary()
        graph.construct_graph_edges()

        is_skip = args.skip or True
        is_random = args.random or False
        required_only = args.required_only or True
        n_samples = int(args.n_samples) or 1
        path = args.path

        graph.graph_validation(skip=is_skip)

        graph.simulate_graph_data(
            path=path,
            n_samples=n_samples,
            random=is_random,
            required_only=required_only,
            skip=is_skip,
        )


if __name__ == "__main__":
    main()
