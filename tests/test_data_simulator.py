import os
from pathlib import Path

from datasimulator.graph import Graph
from dictionaryutils import dictionary


def test_get_schema(init_dictionary):
    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()
    assert graph.graph_validation()

    testDataPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "TestData")
    Path(testDataPath).mkdir(parents=True, exist_ok=True)
    graph.simulate_graph_data(path=testDataPath)
    # TODO: currently we just test that the function runs. We should check the generated files too.
