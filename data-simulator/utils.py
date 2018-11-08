import random

from errors import UserError


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