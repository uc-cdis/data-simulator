import sys

from cdislogging import get_logger

from errors import UserError
from generator import (
    generate_hash,
    generate_datetime,
    generate_string_data,
    generate_simple_primitive_data,
)
from utils import is_mixed_type, random_choice, get_recursive_keys


# Ingnore system properties
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


class Node(object):
    """
    Class representation for node
    """

    def __init__(self, node_name, node_schema, project):
        """
        """
        self.name = node_name
        self.project = project
        self.required = node_schema.get("required", [])
        self.sys_properties = node_schema.get("systemProperties", [])
        try:
            self.category = node_schema["category"]
            self.properties = node_schema["properties"]
            self.links = node_schema["links"]
        except KeyError as e:
            raise UserError(
                "Error: NODE {} does not have key `{}`".format(node_name, e.message)
            )
        self.required_links = []
        self.simulated_dataset = []

    def __str__(self):
        return self.name

    @staticmethod
    def _is_link_property(prop_schema):
        keys = get_recursive_keys(prop_schema)
        if "id" in keys and "pattern" in keys and "term" in keys:
            return True
        return False

    @staticmethod
    def _is_datetime_property(prop_schema):
        if str(prop_schema).find("date and time of day") > 0:
            return True
        return False

    @staticmethod
    def _simulate_data_from_simple_schema(prop, simple_schema):
        if simple_schema["data_type"] == "md5sum":
            return generate_hash()
        elif simple_schema["data_type"] == "enum":
            return random_choice(simple_schema["values"])
        elif simple_schema["data_type"] == "datetime":
            return generate_datetime()
        else:
            return generate_simple_primitive_data(
                data_type=simple_schema["data_type"],
                pattern=simple_schema.get("pattern"),
            )

    def node_validation(self, required_only=False):
        """
        Validate the node schema and check if the node is submitable or not.
        The method supports for generating data even when the node does not pass validation.
        Some non-required properties, which can be missed, may fail the validation.

        Args:
            required_only(bool)

        Outputs:
            pass_validation(bool): The node does not pass validation
            is_submitable(bool): The node can be submitted even it does not pass validation
        """
        # if node schema is well-defined
        pass_validation = True
        is_submittable = True

        if len(self.name) > 63:
            logger.error(
                "The name of the node {} is too long. Must less than 64 characters".format(
                    self.name
                )
            )
            pass_validation = False
            is_submittable = False

        # Go through all the properties to collect all possible errors may happend
        for prop in self.required:
            if prop not in self.properties:
                logger.error(
                    "Node {}. Required property {} is not in property list".format(
                        self.name, prop
                    )
                )
                pass_validation = False
                is_submittable = False

        # validate properties
        template = self.construct_property_generator_template(
            required_only=required_only
        )

        for prop, schema in template.iteritems():
            if schema["data_type"] is None:
                logger.error(schema["error_msg"])
                pass_validation = False
                if prop in self.required:
                    is_submittable = False

        return pass_validation, is_submittable

    def construct_property_generator_template(self, required_only=True):
        """
        Construct generator template for non-link properties. This template is
        used to generate data in batch.

        Args:
            required_only(bool): only simulate required properties

        Outputs:
            dict: template for data generator. Ex.
                {
                    'high_range':{
                        'data_type': 'number'
                        },
                    'hash': {
                        'data_type': 'string',
                        'format': '^[0-9a-f]{32}'
                        },
                }

        """

        template = {}

        for prop, prop_schema in self.properties.iteritems():
            if (
                prop in [link["name"] for link in self.required_links]
                or prop in self.sys_properties
                or prop in EXCLUDED_FIELDS
                or (required_only and prop not in self.required)
            ):
                continue

            template[prop] = self.construct_simple_property_schema(
                prop=prop, prop_schema=prop_schema
            )

        return template

    def construct_simple_property_schema(self, prop, prop_schema):
        """
        Construct a simple schema for just single non-link property

        Args:
            prop(str): property name
            prop_schema(json): property schema

        Outputs:
            dict: a simple property schema to build data generator template

        """
        if prop == "md5sum":
            return {"data_type": "md5sum"}

        if prop_schema.get("type"):
            return {
                "data_type": prop_schema.get("type"),
                "pattern": prop_schema.get("pattern"),
            }

        elif prop_schema.get("oneOf") or prop_schema.get("anyOf"):
            one_of = prop_schema.get("oneOf") or prop_schema.get("anyOf")
            for one in one_of:
                if Node._is_link_property(one):
                    return {"data_type": "link_type"}

                data_type = one.get("type")
                if not data_type:
                    continue
                return {"data_type": data_type}

        elif prop_schema.get("enum"):
            if is_mixed_type(prop_schema.get("enum")):
                return {
                    "data_type": None,
                    "error_msg": "Error: {} has mixed datatype. Detail {}".format(
                        prop, prop_schema["enum"]
                    ),
                    "error_type": "DictionaryError",
                }
            else:
                return {"data_type": "enum", "values": prop_schema.get("enum")}

        elif Node._is_datetime_property(prop_schema):
            return {"data_type": "datetime"}

        else:
            return {
                "data_type": None,
                "error_msg": "Node {}. Can not get data type of {}. Detail {}".format(
                    self.name, prop, prop_schema
                ),
                "error_type": "DictionaryError",
            }

    def simulate_data(self, n_samples=1, random=False, required_only=True):
        """
        Simulate data for the current node

        Args:
            n_samples(int): number of samples need to be generated
            random(bool): random links or not
            required_only(bool): generate only required data

        Output:
            simulated_data[list]: list of simulated record
        """
        # skip project node
        if not self.required_links:
            return

        # re compute n-samples base on link type (one_to_one, one_to_many, ..etc.)
        min_required_samples = sys.maxint
        for link_node in self.required_links:
            if link_node["multiplicity"] in {"one_to_one", "one_to_many"}:
                min_required_samples = min(
                    min_required_samples, len(link_node["node"].simulated_dataset)
                )
        n_samples = min(min_required_samples, n_samples)

        simulated_data = []

        # construct template
        template = self.construct_property_generator_template(
            required_only=required_only
        )

        simulated_data = []
        for _ in xrange(n_samples):
            example = {}

            for prop, simple_schema in template.iteritems():
                if simple_schema["data_type"] is None:
                    logger.warn(simple_schema["error_msg"])
                # Skip. Simulate link properties later
                elif simple_schema["data_type"] == "link_type":
                    continue
                else:
                    example[prop] = Node._simulate_data_from_simple_schema(
                        prop, simple_schema
                    )

            example["submitter_id"] = self._simulate_submitter_id()
            example["type"] = self.name

            simulated_data.append(example)

        # simulate link properties
        try:
            self._simulate_link_properties(simulated_data, random)
            # store to dataset
            self.simulated_dataset = simulated_data
        except IndexError:
            # just skip it
            pass

        return simulated_data

    def _simulate_link_properties(self, simulated_data, random=False):
        """
        Simulate data for required links

        Args:
            simulated_data(list): list of data samples need to be filled
            random(bool): whether randomly link to parent nodes

        Outputs:
            None

        Side effects:
            simulated_data(list): simulated_data is updated

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

    def _simulate_submitter_id(self):
        return self.name + "_" + generate_string_data()

    @classmethod
    def simulate_properties_path(cls):
        raise NotImplementedError()
