import logging
from helper import os_validator
from repo import my_enum


def set_logger(func_name):
    file_name = os_validator.get_logpath(func_name)
    logger = logging.getLogger()
    logger.setLevel('INFO')
    BASIC_FORMAT = '%(asctime)s [%(filename)s - %(funcName)s:%(lineno)d] [%(levelname)s] : %(message)s'
    DATE_FORMAT = '%y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(BASIC_FORMAT, datefmt=DATE_FORMAT)

    console_log = logging.StreamHandler()
    console_log.setFormatter(formatter)
    console_log.setLevel("WARNING")
    file_log = logging.FileHandler(file_name, mode='w')
    file_log.setFormatter(formatter)
    logger.addHandler(console_log)
    logger.addHandler(file_log)
    return logger


def helper(index, sleep, qsize, thread_name, url, region):
    # process general list
    general_list = ["#%03d" % index]
    if sleep != 0:
        general_list.append("sleep=%s" % sleep)
    if qsize is not None:
        general_list.append("qsize=%03d" % qsize)
    if thread_name is not None:
        arr = str.split(thread_name, '-')
        general_list.append("%s-%02d" % (arr[0], int(arr[1])))

    general_list[0] = "[" + general_list[0]
    general_list[-1] = general_list[-1] + ']'

    # process other list
    other_list = ["URL=%s" % url]
    if region is not None:
        other_list.append("lb-region=%s" % region)

    return general_list, other_list


def info_handler(url, code, index, sleep=0, qsize=None, thread_name=None, method=my_enum.Method.GET, region=None,
                 waf_ip=None, request_size=None, response_size=None):
    (general, other) = helper(index, sleep, qsize, thread_name, url, region)
    if waf_ip is not None:
        other.append("WAF_ip=%s" % waf_ip)
    if request_size is not None:
        request_size = round(request_size/1024, 2)
        other.append("request_size: %s KB" % request_size)
    if response_size is not None:
        response_size = round(response_size / 1024, 2)
        other.append("response_size: %s KB" % response_size)

    if code is None:
        code = "?"
    state = "[%s=%s]" % (method.value, code)
    log = (state + ", ".join(general)) + " - " + (", ".join(other))
    return log


def error_handler(url, error_msg, index, sleep=0, qsize=None, thread_name=None, method=my_enum.Method.GET, region=None):
    (general, other) = helper(index, sleep, qsize, thread_name, url, region)
    other.append("msg: %s" % error_msg)
    state = "[%s]" % method.value
    log = (state + ", ".join(general)) + " - " + (", ".join(other))
    return log
