import argparse

from dictionaryutils import DataDictionary, dictionary

from graph import Graph


def initialize_dictionary(url):
    dictionary.init(DataDictionary(url=url))


def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="action", dest="action")

    validation_cmd = subparsers.add_parser("validate")

    validation_cmd.add_argument("--url", required=True, help="s3 dictionary link.")

    simulate_data_cmd = subparsers.add_parser("simulate")

    simulate_data_cmd.add_argument("--url", required=True, help="s3 dictionary link.")
    simulate_data_cmd.add_argument(
        "--path", required=True, help="path to save files to"
    )

    simulate_data_cmd.add_argument("--program", required=True)
    simulate_data_cmd.add_argument("--project", required=True)

    simulate_data_cmd.add_argument(
        "--max_samples",
        required=False,
        help="max number of samples for each node",
        default=1,
    )

    simulate_data_cmd.add_argument(
        "--random", help="randomly generate data numbers for nodes", action="store_true"
    )

    simulate_data_cmd.add_argument(
        "--required_only", help="generate only required fields", action="store_true"
    )

    simulate_data_cmd.add_argument(
        "--skip", help="skip raising an exception if get error", action="store_true"
    )

    return parser.parse_args()


# python main.py simulate --url https://s3.amazonaws.com/dictionary-artifacts/bhcdictionary/0.4.3/schema.json --path ./data-simulator/sample_test_data --program DEV --project test
def main():
    args = parse_arguments()

    print("Data simulator initialization ...")
    initialize_dictionary(args.url)

    if args.action == "simulate":
        # Initialize graph
        graph = Graph(dictionary, args.program, args.project)
        graph.generate_nodes_from_dictionary()
        graph.construct_graph_edges()

        max_samples = int(args.max_samples)

        # just print error messages
        graph.graph_validation(required_only=args.required_only)

        # simulate data no matter what the graph passes validation or not
        graph.simulate_graph_data(
            path=args.path,
            n_samples=max_samples,
            random=args.random,
            required_only=args.required_only,
            skip=args.skip,
        )
    elif args.action == "validate":
        graph = Graph(dictionary, "DEV", "test")
        graph.generate_nodes_from_dictionary()
        graph.construct_graph_edges()
        graph.graph_validation()


if __name__ == "__main__":
    main()
