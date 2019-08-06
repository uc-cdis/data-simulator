import json

from os.path import join
from subgroup_parser import create_subgroup_validators
from datasimulator.generator import generate_string_data
from links_simulator import generate_links
from datasimulator.dd_utils import get_properties
from node_simulator import construct_simple_property_schema, _simulate_data_from_simple_schema
from cdislogging import get_logger

logger = get_logger("DataSimulator")


nodes_by_node_name = {}
child_to_parent = {}


EXCLUDED_FIELDS = [
    "type",
    "error_type",
    "state",
    "id",
    "file_state",
    "state",
    "state_comment",
    "project_id",
    "submitter_id",
    "object_id",
    "created_datetime",
    "updated_datetime",
]


def simulate_tree(model, graph, outpath):
    for n in graph.nodes:
        print 'NODE: {}'.format(n)
        simulate_relations(model, graph.dictionary, n)
    print graph.dictionary.schema.keys()
    for n in graph.nodes:
        simulate_nodes_properties(model, graph.dictionary, n)
        l_n = nodes_by_node_name[n.name].values()
        with open(join(outpath, '{}.json'.format(n.name)), 'w') as outfile:
            json.dump(l_n, outfile, indent=4, sort_keys=True)


def simulate_relations(model, dictionary, graph_node):
    required_validator, existing_list, exclusive_list = create_subgroup_validators(dictionary, graph_node.name)
    data_nodes = {}
    for i in xrange(0, graph_node.number):
        key = random_submitter_id(graph_node.name)
        if graph_node.name == 'project':
            data_nodes[key] = {'code': key}
        else:
            data_nodes[key] = {'submitter_id': key}
    nodes_by_node_name[graph_node.name] = data_nodes

    generate_links(model, nodes_by_node_name, graph_node.name, graph_node, exclusive_list)


def simulate_node_properties(props, properties, node_name, data_node):
    for k, v in props.items():
        prop_schema = construct_simple_property_schema(node_name, k, properties[k])
        if prop_schema is None:
            continue
        if prop_schema["data_type"] is None:
            logger.warn(prop_schema["error_msg"])
        # Skip. Simulate link properties later
        elif prop_schema["data_type"] == "link_type":
            continue
        else:
            data_node[k] = _simulate_data_from_simple_schema(prop_schema)


def simulate_nodes_properties(model, dictionary, graph_node):
    print 'Properties of node {}'.format(graph_node.name)
    props = {k: v for (k, v) in get_properties(model, graph_node.name).items() if k not in EXCLUDED_FIELDS}
    properties = dictionary.schema[graph_node.name]['properties']

    for k, v in nodes_by_node_name[graph_node.name].items():
        if len(nodes_by_node_name[graph_node.name]) == 0:
            continue
        simulate_node_properties(props, properties, graph_node.name, v)


def random_submitter_id(name):
    return name + "_" + generate_string_data()
