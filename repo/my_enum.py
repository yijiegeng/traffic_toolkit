from enum import Enum, unique


@unique
class Method(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"


@unique
class Mode(Enum):
    normal = "Normal"
    fast = "Fast"
    attack_slow = "Attack-slow"
    attack_fast = "Attack-fast"
    env_slow = "Env-slow"
    env_fast = "Env-fast"
    getfile = "Get_file"
    postfile = "Post_file"
    getfile_env = "Get_file-env"
    postfile_env = "Post_file-env"


def method_standardize(candidate):
    if candidate is None: return Method.GET
    candidate = str.lower(candidate)
    for method in Method:
        if candidate == str.lower(method.value):
            return method
    raise Exception("[%s] Method Not Found!" % candidate)
