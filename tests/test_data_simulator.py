import os
from pathlib import Path

from datasimulator.graph import Graph
from dictionaryutils import DataDictionary, dictionary

MOD_DIR = os.path.abspath(os.path.dirname(__file__))


def test_get_schema(default_dictionary):
    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()
    assert graph.graph_validation()

    testDataPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "TestData")
    Path(testDataPath).mkdir(parents=True, exist_ok=True)
    graph.simulate_graph_data(path=testDataPath)
    # TODO: currently we just test that the function runs. We should check the generated files too.
    # TODO: delete generated files at the end of tests


def test_generate_submission_order():
    datadictionary = DataDictionary(
        local_file=os.path.join(MOD_DIR, "schemas/gtex.json")
    )
    dictionary.init(datadictionary)

    graph = Graph(dictionary, "DEV", "test")
    graph.generate_nodes_from_dictionary()
    graph.construct_graph_edges()

    submission_order = [node.name for node in graph.generate_submission_order()]
    assert len(submission_order) == len(
        set(submission_order)
    ), "There should be not duplicates"
    assert submission_order == [
        "project",
        "core_metadata_collection",
        "read_group",
        "submitted_aligned_reads",
        "submitted_unaligned_reads",
        "alignment_workflow",
        "alignment_cocleaning_workflow",
        "aligned_reads",
        "aligned_reads_index",
        "publication",
        "study",
        "subject",
        "demographic",
        "exposure",
        "sample",
        "aliquot",
        "germline_mutation_calling_workflow",
        "simple_germline_variation",
        "imaging_file",
        "imaging_file_reference",
        "electrocardiogram_test",
        "acknowledgement",
        "reference_file",
        "blood_pressure_test",
        "sleep_test_file",
        "reference_file_index",
        "medical_history",
        "cardiac_mri",
        "germline_variation_index",
        "lab_result",
        "medication",
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

    node = [n for n in graph.nodes if n.name == "analyte"][0]
    submission_order = [
        node.name for node in graph.generate_submission_order_path_to_node(node)
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
