import os
import json
import utils

from cdislogging import get_logger

from errors import UserError, DictionaryError, NotSupported
from generator import (
    generate_hash,
    generate_list_numbers,
    generate_datetime,
    generate_string_data,
    generate_simple_primitive_data,
)
from utils import (
    is_mixed_type,
    random_choice, 
    get_recursive_keys,
    get_recursive_values,
)

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
]


logger = get_logger("DataSimulator")

def error_process(do, msg, exc):
    if do == "log":
        logger.error(msg)
    elif do == "raise":
        raise exc(msg)
    else:
        raise NotSupported("{} is not supported".format(type))

class Node(object):
    """
    """

    def __init__(self, node_name, node_schema, project):
        """
        """
        self.name = node_name
        self.project = project
        try:
            self.category = node_schema["category"]
            self.properties = node_schema["properties"]
            self.required = node_schema.get("required", [])
            self.sys_properties = node_schema["systemProperties"]
            self.links = node_schema["links"]
        except KeyError as e:
            raise UserError("Error: NODE {} does not have key `{}`".format(node_name, e.message))
        self.required_links = []
        self.childs = []
        self.simulated_dataset = []

    def __str__(self):
        return self.name

    def node_validation(self, skip=True):
        """
        """
        for prop in self.required:
            if prop not in self.properties:
                error_process(
                    do="log" if skip else "raise",
                    msg="Node {}. Required property {} is not in property list".format(
                        self.name, prop
                    ),
                    exc=DictionaryError,
                )

        if not self.required_links and self.name != "project":
            error_process(
                do="log" if skip else "raise",
                msg="Node {} does not have any required link".format(self.name),
                exc=DictionaryError,
            )

    def _simulate_link_data(self, simulated_data, random=False):
        """
        simulate data for required links

        Args:
            simulated_data(list): list of data samples need to be filled with new data
            random(bool): whether randomly link to parent nodes
            skip(bool): whether continue or break if get error
        
        Output:
            None
        
        Side effect:
            simulated_data(list): updated simulated_data
        
        """

        for link_node in self.required_links:
            for idx, sample in enumerate(simulated_data):
                if link_node["name"] == "projects":
                    sample[link_node["name"]] = {"code": self.project}
                    continue

                if link_node["multiplicity"] in {"many_to_one", "many_to_many"}:
                    if random:
                        choosen_sample = random_choice(
                            link_node["node"].simulated_dataset
                        )
                    else:
                        choosen_sample = link_node["node"].simulated_dataset[idx]

                    if choosen_sample:
                        sample[link_node["name"]] = {
                            "submitter_id": choosen_sample["submitter_id"]
                        }
                else:
                    sample[link_node["name"]] = {
                        "submitter_id": link_node["node"].simulated_dataset[idx][
                            "submitter_id"
                        ]
                    }

    def _simulate_non_link_properties_data(self, required_only=True, skip=True):
        """
        simulate data for properties other than links
        """

        sample = {}
        for prop, prop_schema in self.properties.iteritems():
            if prop in [link['name'] for link in self.required_links] or prop in self.sys_properties:
                continue
            if prop in EXCLUDED_FIELDS or (required_only and prop not in self.required):
                continue

            single_property_data = self.simulate_data_for_single_property(
                prop, prop_schema
            )
            if single_property_data is not None:
                sample[prop] = single_property_data
            else:
                if prop in self.required:
                    error_process(
                        do="log" if skip else "raise",
                        msg='Can not simulate required property {}. Node {}'.format(prop, self.name),
                        exc=DictionaryError,
                    )

        return sample

    def _simulate_submitter_id(self):
        return self.name + "_" + generate_string_data()

    def simulate_data(self, n_samples=1, random=False, required_only=True, skip=True):
        """
        Simulate data for the node
        """
        if not self.required_links:
            return

        min_required_samples = 1.0e6

        for link_node in self.required_links:
            if link_node["multiplicity"] in {"one_to_one", "one_to_many"}:
                min_required_samples = min(
                    min_required_samples, len(link_node["node"].simulated_dataset)
                )

        n_samples = min(min_required_samples, n_samples)

        simulated_data = []

        for _ in xrange(n_samples):
            example = self._simulate_non_link_properties_data(required_only=required_only, skip=skip)
            example["submitter_id"] = self._simulate_submitter_id()
            
            example["type"] = self.name
            simulated_data.append(example)
    
        self._simulate_link_data(simulated_data, random)

        # store in dataset
        self.simulated_dataset += simulated_data
        
        return simulated_data

    @staticmethod
    def _is_link_property(prop_schema):
        keys = get_recursive_keys(prop_schema)
        if "id" in keys and "pattern" in keys and "term" in keys:
            return True
        return False
    
    @staticmethod
    def _is_datetime_property(prop_schema):
        if str(prop_schema).find('date and time of day') > 0:
            return True
        return False

    def simulate_data_for_single_property(self, prop, prop_schema, is_required=False):
        """
        Simulate data for single property
        """
        # if prop == 'file_size' and self.name == 'expression_array_file':
        #     import pdb; pdb.set_trace()
        #     import pdb; pdb.set_trace()
        try:
            if prop == "md5sum":
                return generate_hash()
            if prop_schema.get("type"):
                return generate_simple_primitive_data(
                    prop_schema.get("type"), prop_schema.get("pattern")
                )
            elif prop_schema.get("oneOf") or prop_schema.get("anyOf"):
                one_of = prop_schema.get("oneOf") or prop_schema.get("anyOf")
                for one in one_of:
                    if Node._is_link_property(one):
                        return None

                    data_type = one.get("type")
                    if not data_type:
                        continue
                    return generate_simple_primitive_data(data_type)
            elif prop_schema.get("enum"):
                if is_mixed_type(prop_schema.get("enum")):
                    logger.error(
                        "Error: {} has mixed datatype. Detail {}".format(
                            prop, prop_schema["enum"]
                        )
                    )
                return random_choice(prop_schema.get("enum"))
            elif Node._is_datetime_property(prop_schema):
                return generate_datetime()
            else:
                raise DictionaryError(
                    "Can not simulate prop {}. Schema does not provide enough info. Detail {}".format(
                        prop, prop_schema
                    )
                )

        except UserError as e:
            logger.error("Error: {}".format(e.message))

        return None

    @classmethod
    def simulate_data_path(cls):
        raise NotImplementedError()

    def to_json():
        raise NotImplementedError()
