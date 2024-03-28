import os
from datasimulator.file_handling import write_submission_order_to_file
from datasimulator.node import Node


def test_write_to_file_or_log_error(tmpdir):
    """ asking for tmpdir in the parameter provides an empty test directory for testing """
    node_a = Node(
        'first_node',
        {"category": "foo", "properties": "bar", "links": "biz", "oneOf": "baz"},
        'test_project',
        False)
    node_b = Node(
        'second_node',
        {"category": "aoo", "properties": "aar", "links": "aiz", "oneOf": "aaz"},
        'test_project',
        False)
    submission_order = [node_a, node_b]
    test_path = tmpdir.mkdir("test-data").join("DataImportOrderPath.txt")
    succeeded = write_submission_order_to_file(submission_order, test_path)
    assert succeeded and os.path.getsize(test_path) > 0
