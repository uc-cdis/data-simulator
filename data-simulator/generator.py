import os
import string
import rstr
import random
import utils

from cdislogging import get_logger

from errors import UserError

logger = get_logger('generator')

def generate_string_data(size=10, pattern=None):
    pattern = pattern or '^[0-9a-f]{' + str(size) + '}'
    return rstr.xeger(pattern)


def generate_number(minx=0, maxx=100, is_int=False):
    return random.randint(minx, maxx) if is_int else random.uniform(minx, maxx)


def generate_boolean():
    return random.randint(0, 1) > 0


def generate_did():
    return rstr.xeger(r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$')


def generate_hash():
    return rstr.xeger(r'^[0-9a-f]{32}')


def generate_simple_primitive_data(data_type, pattern=None):
    """
    Generate a single primitive data
    """
    if isinstance(data_type, list):
        if 'null' in data_type:
            data_type.remove('null')
        if not data_type:
            raise UserError("{} contains only null type".format(data_type))
        data_type = data_type[0]

    if data_type == 'string':
        return generate_string_data(pattern=pattern)
    if data_type == 'integer':
        return generate_number(is_int=True)

    if data_type == 'float' or data_type == 'number':
        return generate_number()
    if data_type == 'array':
        return []
   
    if data_type == 'boolean':
        return generate_boolean()
    raise UserError('{} is not supported'.format(data_type))
