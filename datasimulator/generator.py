from datetime import datetime, timedelta
import rstr
import random

from .errors import UserError

tried_words = False
WORDS = None


def generate_string_data(size=10, pattern=None, format=None):
    if format:
        return generate_string_data_with_format(format)

    global tried_words, WORDS
    if not tried_words:
        tried_words = True
        try:
            word_file = "/usr/share/dict/words"
            WORDS = open(word_file).read().splitlines()
        except Exception:
            pass
    if pattern or not WORDS:
        pattern = pattern or "^[0-9a-f]{" + str(size) + "}"
        return rstr.xeger(pattern)
    else:
        return "{}_{}".format(random.choice(WORDS), random.choice(WORDS))


def generate_string_data_with_format(format):
    if format in ["date", "date-time"]:
        min_year = 1980
        max_year = 2020
        start = datetime(min_year, 1, 1, 00, 00, 00)
        years = max_year - min_year + 1
        end = start + timedelta(days=365 * years)
        random_datetime = start + (end - start) * random.random()
        if format == "date":
            return random_datetime.strftime("%Y-%m-%d")
        else:  # date-time
            return random_datetime.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    else:
        raise UserError(
            f"Format '{format}' is not currently supported by data-simulator"
        )


def generate_number(minx=0, maxx=100, is_int=False):
    return random.randint(minx, maxx) if is_int else random.uniform(minx, maxx)


def generate_list_numbers(counts, nmax=100, random=False):
    return [
        generate_number(minx=max(1, int(0.2 * nmax)), maxx=nmax, is_int=True)
        if random
        else nmax
        for _ in range(counts)
    ]


def generate_boolean():
    return bool(random.getrandbits(1))


def generate_hash():
    return generate_string_data(pattern=r"^[0-9a-f]{32}")


def generate_datetime():
    return rstr.xeger(
        r"^\d\d\d\d-(0[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01]) (0[0-9]|1[0-9]|2[0-3]):(0[0-9]|[0-5][0-9]):(0[0-9]|[0-5][0-9])$"
    )


def generate_array_data_type(
    item_type, n_items=1, item_predefined_values=[], pattern=None, format=None
):
    if item_type == "string":
        return [
            generate_string_data(size=10, pattern=pattern, format=format)
            for _ in range(n_items)
        ]
    elif item_type == "integer":
        return [generate_number(is_int=True) for _ in range(n_items)]
    elif item_type in {"float", "number"}:
        return [generate_number() for _ in range(n_items)]
    elif item_type == "enum":
        return [random.choice(item_predefined_values)]
    else:
        raise UserError("Array item type '{}' is not supported".format(item_type))


def generate_simple_primitive_data(
    data_type, pattern=None, maxx=None, minx=None, format=None
):
    """
    Generate a single primitive data
    """
    if data_type == "string":
        return generate_string_data(pattern=pattern, format=format)

    if data_type == "boolean":
        return generate_boolean()

    # format min and max values, we need them for int and float
    minx = minx or 0
    maxx = maxx or 100
    assert isinstance(minx, (int, float)), "minx should be a number (got {})".format(
        minx
    )
    assert isinstance(maxx, (int, float)), "maxx should be a number (got {})".format(
        maxx
    )
    if maxx < minx:
        maxx = minx + 100

    if data_type == "integer":
        return generate_number(is_int=True, maxx=maxx, minx=minx)

    if data_type == "float" or data_type == "number":
        return generate_number(maxx=maxx, minx=minx)

    raise UserError("Data type '{}' is not supported".format(data_type))


def generate_consent_code(size=5):
    pattern = "^[A-Z]{" + str(size) + "}"
    return rstr.xeger(pattern)
