import os

import pytest

from datasimulator.file_handling import write_submission_order_to_file
from datasimulator.node import Node

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
example_submission_order = [node_a, node_b]


def get_contents(test_path):
    with open(test_path, "r") as file:
        contents = file.read()
        return contents


def test_write_to_file_or_log_error_succeeds(tmpdir):
    """ asking for tmpdir in the parameter provides an empty test directory for testing """
    test_path = tmpdir.mkdir("test-data").join("DataImportOrderPath.txt")
    succeeded = write_submission_order_to_file(example_submission_order, test_path)
    assert succeeded and os.path.getsize(test_path) > 0 and get_contents(test_path) == 'first_node\tfoo\nsecond_node\taoo\n'


def test_write_to_file_or_log_error_fails():
    """ Tests that write_submission_order_to_file fails when the directory does not exist"""
    with pytest.raises(IOError):
        write_submission_order_to_file(example_submission_order, "/test-path")
