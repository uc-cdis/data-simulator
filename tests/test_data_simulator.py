import os
from pathlib import Path

from datasimulator.graph import Graph
from dictionaryutils import DataDictionary, dictionary

MOD_DIR = os.path.abspath(os.path.dirname(__file__))


def test_get_schema(default_dictionary):
    """Tests graph successfully generates notes & links (is validated) and
    that the graph data simulation function runs"""
    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()
    assert graph.graph_validation()

    testDataPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "TestData")
    Path(testDataPath).mkdir(parents=True, exist_ok=True)
    graph.simulate_graph_data(path=testDataPath)
    # TODO: currently we just test that the function runs. We should check the generated files too.
    # TODO: delete generated files at the end of tests


def test_local_get_schema(default_dictionary):
    """Tests files are successfully generated & deletes generated files at the end of test."""
    # Set up test (Check local test folder is empty)
    local_test_path = "tests/TestDataTemp"
    assert len(os.listdir(local_test_path)) == 0

    # Confirm test folder is empty
    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()
    assert graph.graph_validation()
    graph.simulate_graph_data(path=local_test_path)

    # Check that files generated (should match files from tests/schema/default)
    default_schema_files = os.listdir("tests/schemas/default")
    default_schema_files_filtered = [
        x.split(".")[0]
        for x in default_schema_files
        if (not x.startswith("_") and not x.startswith("program"))
    ]
    test_generated_files = os.listdir(local_test_path)
    test_generated_files_filtered = [
        x.split(".")[0]
        for x in test_generated_files
        if not (x == "DataImportOrder.txt")
    ]
    assert sorted(default_schema_files_filtered) == sorted(
        test_generated_files_filtered
    )

    # Detele generated files at the end of the tests
    for file in test_generated_files:
        os.remove(local_test_path + f"/{file}")


def test_generate_submission_order():
    """
    Generate the submission order from the project node to all leaf nodes.
    Check that parent nodes are always submitted before their linked child nodes.
    """
    datadictionary = DataDictionary(
        local_file=os.path.join(MOD_DIR, "schemas/gtex.json")
    )
    dictionary.init(datadictionary)

    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()

    submission_order = graph.generate_submission_order()
    names = [node.name for node in submission_order]
    assert len(names) == len(
        set(names)
    ), "There should be not duplicates in the submission order"

    for node in submission_order:
        node_i = submission_order.index(node)
        for child_node in node.child_nodes:
            child_i = submission_order.index(child_node)
            assert (
                node_i < child_i
            ), f"Node '{node.name}' should be submitted before its child '{child_node.name}'"

    assert names == [
        "project",
        "publication",
        "study",
        "core_metadata_collection",
        "acknowledgement",
        "reference_file",
        "reference_file_index",
        "subject",
        "demographic",
        "exposure",
        "electrocardiogram_test",
        "sample",
        "blood_pressure_test",
        "sleep_test_file",
        "medical_history",
        "cardiac_mri",
        "imaging_file",
        "lab_result",
        "medication",
        "imaging_file_reference",
        "aliquot",
        "read_group",
        "submitted_aligned_reads",
        "submitted_unaligned_reads",
        "germline_mutation_calling_workflow",
        "alignment_cocleaning_workflow",
        "alignment_workflow",
        "aligned_reads",
        "aligned_reads_index",
        "simple_germline_variation",
        "germline_variation_index",
    ]


def test_generate_submission_order_path_to_node():
    """
    Generate the submission order from the project node to a specific leaf node.
    Check that parent nodes are always submitted before their linked child nodes.
    """
    datadictionary = DataDictionary(
        local_file=os.path.join(MOD_DIR, "schemas/gtex.json")
    )
    dictionary.init(datadictionary)

    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()

    submission_order = graph.generate_submission_order_path_to_node(
        graph.get_node_with_name("submitted_aligned_reads")
    )
    names = [node.name for node in submission_order]
    assert len(names) == len(
        set(names)
    ), "There should be not duplicates in the submission order"

    for node in submission_order:
        node_i = submission_order.index(node)
        for child_node in node.child_nodes:
            child_i = submission_order.index(child_node)
            assert (
                node_i < child_i
            ), f"Node '{node.name}' should be submitted before its child '{child_node.name}'"

    assert names == [
        "project",
        "study",
        "subject",
        "sample",
        "aliquot",
        "read_group",
        "core_metadata_collection",
        "submitted_aligned_reads",
    ]


def test_generate_submission_order_path_to_node_multiple_children():
    # this is a simplified version of the bpadictionary, where "aliquot" is child of both "sample" and "study",
    # and "case" is child of "study". So "study" should be submitted before both "aliquot" and "case", and not
    # in-between.
    datadictionary = DataDictionary(
        local_file=os.path.join(MOD_DIR, "schemas/multiple_children_edge_case.json")
    )
    dictionary.init(datadictionary)

    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()

    submission_order = [
        node.name
        for node in graph.generate_submission_order_path_to_node(
            graph.get_node_with_name("analyte")
        )
    ]

    # before the fix, "study" was not submitted before "case":
    # ['project', 'case', 'biospecimen', 'sample', 'study', 'aliquot', 'analyte']
    assert submission_order == [
        "project",
        "study",
        "case",
        "biospecimen",
        "sample",
        "aliquot",
        "analyte",
    ]
