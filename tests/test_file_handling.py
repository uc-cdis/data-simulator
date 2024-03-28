from datasimulator.graph import Graph
from dictionaryutils import dictionary
from datasimulator.file_handling import write_to_file_or_log_error
from datasimulator.utils import attempt

def test_write_to_file_or_log_error():
    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()
    submission_order = graph.generate_submission_order()
    file_path = "test-da/DataImportOrderPath.txt"
    output = write_to_file_or_log_error(file_path, submission_order)
    assert False
