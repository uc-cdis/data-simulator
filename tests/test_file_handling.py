import os
from datasimulator.graph import Graph
from dictionaryutils import dictionary
from datasimulator.file_handling import write_to_file_or_log_error


def test_write_to_file_or_log_error(tmpdir):
    """ asking for tmpdir in the parameter provides an empty test directory for testing """
    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()
    submission_order = graph.generate_submission_order()
    test_path = tmpdir.mkdir("test-data").join("DataImportOrderPath.txt")
    succeeded = write_to_file_or_log_error(test_path, submission_order)
    assert succeeded and os.path.getsize(test_path) > 0
