import os
import json
import utils
from cdislogging import get_logger

from errors import UserError, DictionaryError
from generator import (
    generate_hash,
    generate_string_data,
    generate_simple_primitive_data,
)
from utils import (
    is_mixed_type,
    random_choice,
)
logger = get_logger('DataSimulator')

# from datamodelutils import models
EXCLUDED_NODE = ['program', 'root']

EXCLUDED_FIELDS = ["type", "error_type", "state", "id",
                   "file_state", "created_datetime", "updated_datetime",
                   "state", "state_comment", "project_id", "submitter_id",
                   "workflow_start_datetime", "workflow_end_datetime",
                   "sequencing_date", "run_datetime", "object_id"]


class Graph(object):
    """
    """

    # should be empty graph
    def __init__(self, dictionary, program, project):
        self.dictionary = dictionary
        self.root = None
        self.program = program
        self.project = project
        self.nodes = []

    def prelimary_dictionary_check(self):
        if self.dictionary is None:
            raise UserError('Dictionary is not initialized!!!')
        return True

    def _get_list_of_node_names(self):
        return [
            k for k in self.dictionary.schema if k not in EXCLUDED_NODE
        ]

    def generate_nodes_from_dictionary(self, random=True):
        logger.info('Start simulating data')
        for node_name in self._get_list_of_node_names():
            node = Node(node_name, self.dictionary.schema[node_name], self.project)
            if node_name == 'project':
                self.root = node
            self.nodes.append(node)


    def test_simulatation(self):
        node_order = self.gen_submission_order_v2()
        with open('./sample_test_data/DataImportOrder.txt', 'w') as outfile:
            for node in node_order:
                outfile.write(node.name+'\n')
        for node in node_order:
            logger.info("start simulating data for node {}".format(node.name))
            node.simulate_data(save=True)
            for data in node.simulate_dataset:
                with open('./sample_test_data/' + node.name + ".json", 'w') as outfile:
                    if node.name == 'derived_checkup':
                        import pdb; pdb.set_trace()
                    json.dump(data, outfile, indent=4, sort_keys=True)
        

    def get_node_with_name(self, node_name):
        for node in self.nodes:
            if node.name == node_name:
                return node
        return None

    def _add_parent_to_node(self, node, parent_name, link_name, multiplicity=None):
        # skip all the links to Project node
        if parent_name in EXCLUDED_NODE:
            return
        node_parent = self.get_node_with_name(parent_name)
        if not node_parent:
            raise UserError("Node {} have a link to node {} which does not exist".format(node.name, parent_name))
        
        node.parents.append({'node': node_parent, 'multiplicity': multiplicity, 'name': link_name})
        node_parent.childs.append(node)

    def generate_full_graph(self):

        # Link nodes together to create graph
        for node in self.nodes:
            if node == self.root:
                continue
            if not node.links:
                logger.error('ERROR: {} should have at least one link to other node'.format(node.name))
            try:
                links = node.links
                for link in links:

                    link_tmp = link
                    if not isinstance(link, list):
                        link_tmp = [link]
                    for l in link_tmp:
                        if 'target_type' in l:
                            self._add_parent_to_node(node, l['target_type'], l.get('name'), l.get('multiplicity'))
   
                    if 'sub_group' in link or 'subgroup' in link:
                        sub_links = link.get('sub_group') or link.get('subgroup')
                        for sub_link in sub_links:
                            if 'target_type' in sub_link:
                                self._add_parent_to_node(node, sub_link['target_type'], sub_link.get('name'), sub_link.get('multiplicity'))

            except TypeError as e:
                logger.error('Node {} have non-list links. Detail {}'.format(node.name, e.message))

    def gen_submission_order(self):

        print("==========start gen submission order========")
        if not self.root:
            return []
        order_submission = []
        visited = set()
        queue = [self.root]
        index = 0
        while index < len(queue):
            cur_node = queue[index]
            visited.add(cur_node.name)
            order_submission.append(cur_node)
            print(len(order_submission))
            for node in cur_node.childs:
                if node not in queue:
                    queue.append(node)
            index = index + 1
        print("==========end gen submission order========")
        return order_submission

    def gen_submission_order_v2(self):
        order_submission = []
        
        for node in self.nodes:
            path = []
            if node in order_submission:
                continue
            while node != self.root and node not in order_submission:
                path.append(node)
                try:
                    node = node.parents[0].get('node')
                except Exception:
                    break
            path.reverse()
            order_submission += path
        return order_submission
            



class Node(object):
    """
    """
    def __init__(self, node_name, node_schema, project):
        """
        """
        self.name = node_name
        self.project = project
        try:
            self.category = node_schema['category']
            self.properties = node_schema['properties']
            self.required = node_schema['required']
            self.links = node_schema['links']
        except ValueError as e:
            raise UserError(
                'Error: NODE {}. Detail {}'.format(node_name, e.message)
            )
        self.parents = []
        self.childs = []
        self.simulate_dataset = []
    
    def __str__(self):
        return self.name

    def is_root(self):
        return not self.parents
    
    def simulate_data(self, n=1, save=False):
        """
        Simulate data for the node
        """
        #import pdb; pdb.set_trace()
        if not self.parents:
            return
        link_node = self.parents[0].get('node')
        link_node_multiplicity = self.parents[0].get('multiplicity')
        link_name = self.parents[0].get('name')
        if link_node_multiplicity == 'one_to_one':
            n = len(link_node.simulate_dataset)

        simulated_data = []
        for _ in xrange(n):
            example = {}
            for prop, prop_schema in self.properties.iteritems():
                if prop in EXCLUDED_FIELDS or prop not in self.required:
                    continue
                single_property_data = self.simulate_data_for_single_property(prop, prop_schema)
                if prop == 'app_checkups':
                    import pdb; pdb.set_trace()
                example[prop] = single_property_data
            example['submitter_id'] = self.name + "_" + generate_string_data()
            example['type'] = self.name
            #import pdb; pdb.set_trace()
            if link_node.name == 'project':
                example[link_name] = {'code': self.project}
            else:
                try:
                    example[link_name] = {'submitter_id': link_node.simulate_dataset[0]['submitter_id']}
                except Exception:
                    import pdb; pdb.set_trace()
                    print('debug')
            simulated_data.append(example)
        if save:
            self.simulate_dataset += simulated_data
        return simulated_data
        
        

    def simulate_data_for_single_property(self, prop, prop_schema):
        """
        Simulate data for single property
        """
        try:
            if prop == 'app_checkups':
                import pdb; pdb.set_trace()
            if prop == 'md5sum':
                return generate_hash()
            if prop_schema.get('type'):
                return generate_simple_primitive_data(prop_schema.get('type'), prop_schema.get('pattern'))
            elif prop_schema.get('oneOf') or prop_schema.get('anyOf'):
                one_of = prop_schema.get('oneOf') or prop_schema.get('anyOf')
                for one in one_of:
                    data_type = one.get('type')
                    if not data_type:
                        continue
                    return generate_simple_primitive_data(data_type)
                return generate_simple_primitive_data('array')
            elif prop_schema.get('enum'):
                if is_mixed_type(prop_schema.get('enum')):
                    logger.error(
                        "Error: {} has mixed datatype. Detail {}"
                        .format(prop, prop_schema['enum'])
                        )
                return random_choice(prop_schema.get('enum'))
            else:
                logger.error("Error: {} does not have type or enum properties. Schema {}".format(prop, prop_schema))

        except UserError as e:
            logger.error("Error: {}".format(e.message))

        return None

    @classmethod
    def simulate_data_path(cls):
        raise NotImplementedError()

    def to_json():
        raise NotImplementedError()
