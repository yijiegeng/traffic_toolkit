from enum import Enum, unique


@unique
class Method(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"


def enum_standardize(candidate):
    if candidate is None: return Method.GET
    candidate = str.lower(candidate)
    for method in Method:
        if candidate == str.lower(method.value):
            return method
    raise Exception("[%s] Method Not Found!" % candidate)

