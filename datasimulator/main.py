import os
import argparse

from cdislogging import get_logger
from dictionaryutils import DataDictionary, dictionary

from datasimulator.graph import Graph
from datasimulator.submit_data_utils import submit_test_data
from datasimulator.file_handling import write_submission_order_to_file

logger = get_logger("data-simulator", log_level="info")


def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="action", dest="action")

    submission_order_cmd = subparsers.add_parser("submission_order")
    submission_order_cmd.add_argument(
        "--url", required=True, help="s3 dictionary link.", nargs="?"
    )
    submission_order_cmd.add_argument(
        "--node_name", required=False, help="node to generate the submission order for"
    )
    submission_order_cmd.add_argument(
        "--path", required=True, help="path to save file to"
    )

    validation_cmd = subparsers.add_parser("validate")
    validation_cmd.add_argument("--url", required=True, help="s3 dictionary link.")

    simulate_data_cmd = subparsers.add_parser("simulate")
    simulate_data_cmd.add_argument(
        "--url", required=False, help="s3 dictionary link.", nargs="?", default=None
    )
    simulate_data_cmd.add_argument(
        "--path", required=True, help="path to save files to", nargs="?"
    )

    simulate_data_cmd.add_argument(
        "--program", required=False, nargs="?", default="DEV"
    )
    simulate_data_cmd.add_argument(
        "--project", required=False, nargs="?", default="test"
    )

    simulate_data_cmd.add_argument(
        "--max_samples",
        required=False,
        help="max number of samples for each node",
        default=1,
        nargs="?",
    )

    simulate_data_cmd.add_argument(
        "--node_num_instances_file",
        required=False,
        help="max number of samples for each node stored in a file",
        nargs="?",
    )

    simulate_data_cmd.add_argument(
        "--random", help="randomly generate data numbers for nodes", action="store_true"
    )

    simulate_data_cmd.add_argument(
        "--required_only", help="generate only required fields", action="store_true"
    )

    simulate_data_cmd.add_argument(
        "--consent_codes",
        help="include generation of random consent codes",
        action="store_true",
    )

    simulate_data_cmd.add_argument(
        "--skip", help="skip raising an exception if gets an error", action="store_true"
    )

    submit_data_cmd = subparsers.add_parser("submitting_data")
    submit_data_cmd.add_argument("--dir", required=True, help="path containing data")
    submit_data_cmd.add_argument("--host", required=True)
    submit_data_cmd.add_argument("--project", required=True)
    submit_data_cmd.add_argument("--chunk_size", default=1)
    submit_data_cmd.add_argument("--access_token_file", required=True)

    return parser.parse_args()


def initialize_graph(dictionary_url, program, project, consent_codes):
    if dictionary_url:
        logger.info("Loading dictionary from url {}".format(dictionary_url))
        dictionary.init(DataDictionary(url=dictionary_url))
    else:
        logger.info("Loading dictionary from installed dictionary")

    logger.info("Initializing graph...")
    if program and project:
        graph = Graph(dictionary, program=program, project=project)
    else:
        logger.info("Using default program name and project code")
        graph = Graph(dictionary)

    if consent_codes:
        graph.generate_nodes_from_dictionary(consent_codes)
    else:
        graph.generate_nodes_from_dictionary()

    graph.construct_graph_edges()

    return graph


def run_simulation(
    graph, data_path, max_samples, node_num_instances_file, random, required_only, skip
):
    max_samples = int(max_samples)

    # just print error messages
    graph.graph_validation(required_only=required_only)

    # simulate data whether the graph passes validation or not
    logger.info("Generating data...")
    graph.simulate_graph_data(
        path=data_path,
        n_samples=max_samples,
        node_num_instances_file=node_num_instances_file,
        random=random,
        required_only=required_only,
        skip=skip,
    )


def run_submission_order_generation(graph, data_path, node_name=None):
    logger.info("Generating data submission order...")
    if node_name:
        node = graph.get_node_with_name(node_name)
        cmc_node = graph.get_node_with_name("core_metadata_collection")
        if not node:
            raise Exception(
                f"Argument 'node_name' is '{node_name}' but this node does not exist"
            )
        submission_order = graph.generate_submission_order_path_to_node(node, cmc_node)
    else:
        submission_order = graph.generate_submission_order()

    file_path = os.path.join(data_path, "DataImportOrderPath.txt")
    path_exists = os.path.exists(data_path)
    if not path_exists:
        raise Exception(
            f"Cannot create file because path does not exist. Here is the path we expect: '{data_path}'"
        )
    else:
        write_submission_order_to_file(submission_order, file_path)


# python main.py simulate --url https://s3.amazonaws.com/dictionary-artifacts/bhcdictionary/0.4.3/schema.json --path ./data-simulator/sample_test_data --program DEV --project test
def main():
    args = parse_arguments()

    if args.action == "submitting_data":
        logger.info("Submitting data...")
        submit_test_data(
            args.host,
            args.project,
            args.dir,
            args.access_token_file,
            int(args.chunk_size),
        )
        logger.info("Done!")
        return

    logger.info("Data simulator initialization...")
    graph = initialize_graph(
        dictionary_url=args.url if hasattr(args, "url") else None,
        program=args.program if hasattr(args, "program") else None,
        project=args.project if hasattr(args, "project") else None,
        consent_codes=args.consent_codes if hasattr(args, "consent_codes") else None,
    )

    if args.action == "simulate":
        run_simulation(
            graph,
            args.path,
            args.max_samples,
            args.node_num_instances_file,
            args.random,
            args.required_only,
            args.skip,
        )

    elif args.action == "validate":
        logger.info("Validating...")
        graph.graph_validation()

    elif args.action == "submission_order":
        run_submission_order_generation(graph, args.path, args.node_name)

    logger.info("Done!")


if __name__ == "__main__":
    main()
