from functools import wraps
from alive_progress import alive_bar
from helper.logger_setter import set_logger
from repo import my_enum


def add_bar(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        if func.__name__ == "counter":
            jobs = args[1]  # def counter(finish_queue, initial_size, bar=None)
            manual = True
        else:
            jobs = args[2].qsize()  # def worker(logger, prefix, work_queue, sleep, ...)
            manual = False
        with alive_bar(jobs, manual=manual) as bar:
            func(*args, **kwargs, bar=bar)
        return

    return wrapped_func


class log_title(object):
    def __init__(self, mode: my_enum.Mode):
        self.mode = mode

    def __call__(self, func):
        @wraps(func)
        def wrapped_func(prefix, *args, **kwargs):
            func_name = func.__name__
            logger = set_logger(func_name)

            url = kwargs.get("url") if "url" in kwargs else ""
            env_name = kwargs.get("env_name")
            repeat_num = kwargs.get("repeat_num")
            thread_num = kwargs.get("thread_num")
            general_log = "<%s> mode, Domain: %s, repeat [%s] times" % (self.mode.value, prefix + url, repeat_num)
            if thread_num is not None:
                general_log += ", with [%s] threads" % thread_num
            if env_name is not None:
                general_log += ", runs on [%s] env regions" % env_name
            logger.info(general_log)
            func(prefix, *args, **kwargs, logger=logger)
            return

        return wrapped_func
