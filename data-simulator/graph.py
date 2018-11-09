import json

from node import Node, logger

from errors import UserError, DictionaryError, NotSupported

from utils import (
    is_mixed_type,
    random_choice,
)

from generator import (
    generate_list_numbers
)

EXCLUDED_NODE = ["program", "root", "data_release"]


class Graph(object):
    """
    """

    def __init__(self, dictionary, program, project):
        self.dictionary = dictionary
        self.root = None
        self.program = program
        self.project = project
        self.nodes = []

    def prelimary_dictionary_check(self):
        if self.dictionary is None:
            raise UserError("Dictionary is not initialized!!!")
        return True

    def _get_list_of_node_names(self):
        return [k for k in self.dictionary.schema if k not in EXCLUDED_NODE]

    def generate_nodes_from_dictionary(self, random=True):
        #logger.info("Start simulating data")
        for node_name in self._get_list_of_node_names():
            node = Node(node_name, self.dictionary.schema[node_name], self.project)
            if node_name == "project":
                self.root = node
            self.nodes.append(node)

    def get_node_with_name(self, node_name):
        for node in self.nodes:
            if node.name == node_name:
                return node
        return None

    def _add_required_link_to_node(
        self, node, parent_name, link_name, multiplicity=None, skip=True
    ):
        # skip all the links to Project node
        if parent_name in EXCLUDED_NODE:
            return
        node_parent = self.get_node_with_name(parent_name)

        if not node_parent:
            error_process(
                do="log" if skip else "raise",
                msg="Node {} have a link to node {} which does not exist".format(
                    node.name, parent_name
                ),
                exc=DictionaryError,
            )

        node.required_links.append(
            {"node": node_parent, "multiplicity": multiplicity, "name": link_name}
        )
        node_parent.childs.append(node)

    def graph_validation(self, skip=True):
        """
        Call to all node validation to validate
        """
        for node in self.nodes:
            node.node_validation(skip)

    def construct_graph_edges(self):

        # Link nodes together to create graph
        for node in self.nodes:
            if node == self.root:
                continue
            if not node.links:
                logger.error(
                    "ERROR: {} should have at least one link to other node".format(
                        node.name
                    )
                )
            try:
                node_links = node.links

                if not isinstance(node_links, list):
                    node_links = [node_links]

                # expect node_links contains list of links
                for link in node_links:
                    if isinstance(link, dict):
                        if not link.get("required"):
                            continue
                        if "target_type" in link:
                            self._add_required_link_to_node(
                                node,
                                link["target_type"],
                                link.get("name"),
                                link.get("multiplicity"),
                            )

                        if "sub_group" in link or "subgroup" in link:
                            sub_links = link.get("sub_group") or link.get("subgroup")
                            if not isinstance(sub_links, list):
                                sub_links = [sub_links]

                            # just pick one of sub-group links
                            for sub_link in sub_links:
                                if "target_type" in sub_link:
                                    self._add_required_link_to_node(
                                        node,
                                        sub_link["target_type"],
                                        sub_link.get("name"),
                                        sub_link.get("multiplicity"),
                                    )
                                    break

            except TypeError as e:
                logger.error(
                    "Node {} have non-list links. Detail {}".format(
                        node.name, e.message
                    )
                )


    def generate_submission_order_path_to_node(self, node, submission_order):
        """
        generate submission order so that the current node can be submitted
        """
        if node in submission_order:
            return
        for linked_node_dic in node.required_links:
            if linked_node_dic["node"] not in submission_order:
                self.generate_submission_order_path_to_node(
                    linked_node_dic["node"], submission_order
                )
        submission_order.append(node)

    def generate_submission_order_whole_graph(self, submission_order):
        for node in self.nodes:
            if node not in submission_order:
                path_order = []
                self.generate_submission_order_path_to_node(node, path_order)
                for item in path_order:
                    if item not in submission_order:
                        submission_order.append(item)

    def simulate_graph_data(self):
        submission_order = []
        self.generate_submission_order_whole_graph(submission_order)
        with open("./sample_test_data/DataImportOrder.txt", "w") as outfile:
            for node in submission_order:
                outfile.write(node.name + "\n")

        n_samples_list = generate_list_numbers(len(submission_order), nmax=10)
        for idx, node in enumerate(submission_order):
            logger.info("start simulating data for node {}".format(node.name))
            node.simulate_data(n_samples=n_samples_list[idx], random=True)
            with open("./sample_test_data/" + node.name + ".json", "w") as outfile:
                json.dump(node.simulated_dataset, outfile, indent=4, sort_keys=True)