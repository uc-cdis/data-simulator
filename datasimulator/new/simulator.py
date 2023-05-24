import json
from os.path import join

from datasimulator.new.subgroup_parser import create_subgroup_validators
from datasimulator.generator import generate_string_data
from datasimulator.new.links_simulator import generate_links
from datasimulator.dd_utils import get_properties
from datasimulator.node import (
    construct_simple_property_schema,
    _simulate_data_from_simple_schema,
)
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


def simulate_tree(model, program, project, graph, outpath):
    for n in graph.nodes:
        print("NODE: {}".format(n))
        simulate_relations(model, graph.dictionary, n, project)
    print(graph.dictionary.schema.keys())
    for n in graph.nodes:
        simulate_nodes_properties(model, graph.dictionary, n, project)
        if n.name != "project":
            l_n = list(nodes_by_node_name[n.name].values())
        else:
            l_n = list(nodes_by_node_name[n.name].values())[0]
        with open(join(outpath, "{}.json".format(n.name)), "w") as outfile:
            json.dump(l_n, outfile, indent=4, sort_keys=True)
    with open(join(outpath, "{}.txt".format("DataImportOrder")), "w") as order_file:
        order_file.writelines(["{}\n".format(n.name) for n in graph.nodes])


def simulate_relations(model, dictionary, graph_node, project_name):
    required_validator, existing_list, exclusive_list = create_subgroup_validators(
        dictionary, graph_node.name
    )
    data_nodes = {}
    for i in range(0, graph_node.number):
        if graph_node.name == "project" or graph_node.name == "node_project":
            data_nodes[project_name] = {"code": project_name}
        else:
            key = random_submitter_id(graph_node.name)
            data_nodes[key] = {"submitter_id": key}
    nodes_by_node_name[graph_node.name] = data_nodes

    generate_links(
        model, nodes_by_node_name, graph_node.name, graph_node, exclusive_list
    )


def simulate_node_project(props, properties, data_node, project_name):
    data_node["type"] = "project"
    for prop in props.keys():
        prop_schema = construct_simple_property_schema(
            "project", prop, properties[prop]
        )
        if prop_schema is None:
            continue
        if prop_schema["data_type"] is None:
            logger.warning(prop_schema["error_msg"])
        # Skip. Simulate link properties later
        elif prop == "name":
            data_node[prop] = project_name
        elif prop == "code":
            continue
        else:
            data_node[prop] = _simulate_data_from_simple_schema(prop_schema)


def simulate_node_properties(props, properties, node_name, data_node):
    data_node["type"] = node_name
    for prop in props.keys():
        prop_schema = construct_simple_property_schema(
            node_name, prop, properties[prop]
        )
        if prop_schema is None:
            continue
        if prop_schema["data_type"] is None:
            logger.warning(prop_schema["error_msg"])
        # Skip. Simulate link properties later
        elif prop_schema["data_type"] == "link_type":
            continue
        else:
            data_node[prop] = _simulate_data_from_simple_schema(prop_schema)


def simulate_nodes_properties(model, dictionary, graph_node, project_name):
    print("Properties of node {}".format(graph_node.name))
    props = {
        k: v
        for (k, v) in get_properties(model, graph_node.name).items()
        if k not in EXCLUDED_FIELDS
    }
    properties = dictionary.schema[graph_node.name]["properties"]

    for v in nodes_by_node_name[graph_node.name].values():
        if len(nodes_by_node_name[graph_node.name]) == 0:
            continue
        if graph_node.name == "project":
            simulate_node_project(props, properties, v, project_name)
        else:
            simulate_node_properties(props, properties, graph_node.name, v)


def random_submitter_id(name):
    return name + "_" + generate_string_data()
