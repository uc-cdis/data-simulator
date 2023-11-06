import os
import random
import json
from functools import reduce

from .errors import UserError


def is_mixed_type(arr):
    # An enum is said "mixed type" if the enum items don't all have the same type. The only
    # exception to this is NoneType, which is allowed in enums regardless of the type of other
    # items. This allows us to set the value to None when the property is not required.
    if arr:
        return any(not isinstance(e, type(arr[0])) and e != None for e in arr)
    return False


def random_choice(arr):
    if arr:
        return random.choice(arr)
    return None


def is_primitive_type(data):
    return isinstance(data, (int, float, str))


def get_keys_list(d):
    def get_field(d, fields):
        return reduce(lambda acc, field: acc.get(field, {}), fields, d)

    result = []
    to_visit = [[key] for key in d.keys()]
    while to_visit:
        key = to_visit.pop()
        result.append(key[-1])
        value = get_field(d, key)
        if isinstance(value, dict):
            to_visit.extend([key + [next_key] for next_key in value.keys()])
    return result


def generate_list_numbers_from_file(data_file, submission_order, n_samples):
    result = []

    try:
        with open(data_file) as f:
            data = json.load(f)
            for filename in submission_order:
                if str(filename) in data:
                    result.append(data[str(filename)])
                else:
                    result.append(n_samples)

    except IOError:
        raise UserError("file {} does not exist".format(data_file))
    except ValueError:
        raise UserError("Can not load json file {}".format(data_file))
    except KeyError as e:
        raise UserError(
            "Missing node in file {}. Detail {}".format(data_file, e.message)
        )

    return result


def get_graph_traversal_path(direction, start_node):
    """
    Starting from the specified node, step through the graph either from top to bottom (direction=down) or
    from bottom to top (direction=up) through node links, and return the resulting path. Ensure "parent"
    nodes are always before their direct and indirect "child" nodes in the path.

    Args:
        direction(str): "down" for top-to-bottom or "up" for bottom-to-top
        start_node(Node): Node at which to start the path

    Outputs:
        list[Node]: path
    """
    if direction not in ["down", "up"]:
        raise Exception(
            f"Graph traversal is either top-to-bottom (direction=down) or bottom-to-top (direction=up). Provided value direction={direction} unknown."
        )

    to_visit = [start_node]
    path = [start_node]
    while to_visit:
        node = to_visit.pop()
        if direction == "down":
            links = node.child_nodes
        elif direction == "up":
            links = [link["node"] for link in node.required_links]
        for linked_node in links:
            if linked_node in path:
                path.remove(linked_node)
            path.append(linked_node)
            if linked_node not in to_visit:
                to_visit.append(linked_node)

    return path
