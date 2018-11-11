import json
from os.path import join

from node import Node, logger
from errors import UserError, DictionaryError, NotSupported
from utils import is_mixed_type, random_choice
from generator import generate_list_numbers

EXCLUDED_NODE = ["program", "root", "data_release"]


class Graph(object):
    """
    Graph representation class
    """

    def __init__(self, dictionary, program, project):
        """
        Graph constructor

        Args:
            dictionary(str): dictionary url
            program(str): program name
            project(str): project name

        Outputs:
            None
        """
        self.dictionary = dictionary
        self.root = None
        self.program = program
        self.project = project
        self.nodes = []

    def prelimary_dictionary_check(self):
        """
        raise exception if dictionary has not initialized yet
        """
        if self.dictionary is None:
            raise UserError("Dictionary is not initialized!!!")
        return True

    def _get_list_of_node_names(self):
        """
        return a list of node names
        """
        return [k for k in self.dictionary.schema if k not in EXCLUDED_NODE]

    def generate_nodes_from_dictionary(self):
        """
        generate nodes from dictionary

        """
        # logger.info('Start simulating data')
        for node_name in self._get_list_of_node_names():
            node = Node(node_name, self.dictionary.schema[node_name], self.project)
            if node_name == "project":
                self.root = node
            self.nodes.append(node)

    def get_node_with_name(self, node_name):
        """
        get node object given name

        Args:
            node_name(str): node name

        Outputs:
            Node: node object
        """
        for node in self.nodes:
            if node.name == node_name:
                return node
        return None

    def _add_required_link_to_node(
        self, node, link_node_name, link_name, multiplicity=None, skip=True
    ):
        """
        assign required links to a node

        Args:
            node(Node): node object
            link_node_name(str): link node name
            multiplicity(str): link type (one_to_one, one_to_many, ..etc.)
            skip(bool): skip raising an exception to terminate
        
        Outputs:
            None or raise exception
        
        """
        # skip all the links to Project node
        if link_node_name in EXCLUDED_NODE:
            return
        node_parent = self.get_node_with_name(link_node_name)

        if not node_parent:
            error_process(
                do="log" if skip else "raise",
                msg="Node {} have a link to node {} which does not exist".format(
                    node.name, link_node_name
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
        """
        Construct edges between nodes. Ignore option links
        """

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
                raise DictionaryError(
                    "Node {} have non-list links. Detail {}".format(
                        node.name, e.message
                    )
                )

    def generate_submission_order_path_to_node(self, node, submission_order):
        """
        Generate submission order so that the current node can be submitted

        Args:
            node(Node): current node object
            submission_order(list): submission order list 
        
        Outputs:
            None
        
        Side effects:
            submission_order is updated interatively
    
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
        """
        Generate submission order for the graph
        
        Args:
            submission_order(list): submission order list 
        
        Outputs:
            None
        
        Side effects:
            submission_order is updated interatively
        """
        for node in self.nodes:
            if node not in submission_order:
                path_order = []
                self.generate_submission_order_path_to_node(node, path_order)
                for item in path_order:
                    if item not in submission_order:
                        submission_order.append(item)

    def simulate_graph_data(
        self, path, n_samples=1, random=True, required_only=True, skip=True
    ):
        """
        Simulate data for the whole graph

        Args:
            random(bool): whether randomly link to parent nodes
            required_only(bool): only simulate required properties
            skip(bool): skip raising an exception to terminate
        
        Outputs:
            None or raise an exception
        """
        submission_order = []
        self.generate_submission_order_whole_graph(submission_order)
        with open(join(path, "DataImportOrder.txt"), "w") as outfile:
            for node in submission_order:
                outfile.write(node.name + "\n")

        n_samples_list = generate_list_numbers(
            len(submission_order), nmax=n_samples, random=random
        )
        for idx, node in enumerate(submission_order):
            logger.info("start simulating data for node {}".format(node.name))
            node.simulate_data(
                n_samples=n_samples_list[idx],
                random=random,
                required_only=required_only,
                skip=skip,
            )
            with open(join(path, node.name + ".json"), "w") as outfile:
                json.dump(node.simulated_dataset, outfile, indent=4, sort_keys=True)
