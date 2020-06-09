import random
from datasimulator.generator import (
    generate_hash,
    generate_datetime,
    generate_string_data,
    generate_array_data_type,
    generate_simple_primitive_data,
)
from datasimulator.utils import is_mixed_type, random_choice, get_keys_list
from cdislogging import get_logger

logger = get_logger("DataSimulator")


def _is_datetime_property(prop_schema):
    if str(prop_schema).find("date and time of day") > 0:
        return True
    return False


def _is_link_property(prop_schema):
    keys = get_keys_list(prop_schema)
    if "id" in keys and "pattern" in keys and "term" in keys:
        return True
    return False


def construct_simple_property_schema(node_name, prop, prop_schema):
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
        if prop_schema.get("type") == "array":

            if "items" in prop_schema and "enum" in prop_schema["items"]:
                return {
                    "data_type": "array",
                    "item_type": "enum",
                    "item_enum_data": prop_schema["items"]["enum"],
                }

            if prop_schema.get("items") is None or (
                prop_schema.get("items").get("type") is None
            ):
                return {
                    "data_type": "array",
                    "error_msg": "Error: {} has no item datatype. Detail {}".format(
                        prop, prop_schema
                    ),
                    "error_type": "DictionaryError",
                }
            return {
                "data_type": prop_schema.get("type"),
                "item_type": prop_schema.get("items").get("type"),
            }
        else:
            return {
                "data_type": prop_schema.get("type"),
                "pattern": prop_schema.get("pattern"),
                "max": prop_schema.get("maximum", 100),
                "min": prop_schema.get("minimum", 0),
            }

    elif prop_schema.get("oneOf") or prop_schema.get("anyOf"):
        one_of = prop_schema.get("oneOf") or prop_schema.get("anyOf")
        for one in one_of:
            if _is_link_property(one):
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

    elif _is_datetime_property(prop_schema):
        return {"data_type": "datetime"}

    else:
        return {
            "data_type": None,
            "error_msg": "Node {}. Can not get data type of {}. Detail {}".format(
                node_name, prop, prop_schema
            ),
            "error_type": "DictionaryError",
        }


def _simulate_data_from_simple_schema(simple_schema):
    if simple_schema["data_type"] == "md5sum":
        return generate_hash()
    elif simple_schema["data_type"] == "enum":
        return random_choice(simple_schema["values"])
    elif simple_schema["data_type"] == "datetime":
        return generate_datetime()
    elif simple_schema["data_type"] == "array":
        return generate_array_data_type(
            item_type=simple_schema.get("item_type"),
            n_items=1,
            item_predefined_values=simple_schema.get("item_enum_data", []),
        )
    else:
        return generate_simple_primitive_data(
            data_type=simple_schema["data_type"],
            pattern=simple_schema.get("pattern"),
            maxx=simple_schema.get("max"),
            minx=simple_schema.get("min"),
        )
