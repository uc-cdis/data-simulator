import random
from functools import reduce


def is_mixed_type(arr):
    if arr:
        return any(not isinstance(e, type(arr[0])) for e in arr)
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
