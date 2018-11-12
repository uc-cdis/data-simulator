import os

import pytest

from datasimulator.graph import Graph
from dictionaryutils import dictionary


def test_get_schema(init_dictionary):
    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()
    assert graph.graph_validation()
