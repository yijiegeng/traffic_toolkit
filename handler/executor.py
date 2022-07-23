from handler.singlethread_handler import normal_run
from handler.multithread_handler import threads_run
from repo import my_enum, my_node
from repo.attack_info import attack_url_list
from helper import os_validator, info_getter
from helper import decorator


"""
class requestNode:
    def __init__(self, url, para='', method=Method.GET, waf_ip=None, src_ip=None, agent=None, host=None, region=None, 
                 repeat_id=0)

def normal_run(prefix, request_list=None, repeat_num=1, sleep=0, logger=None, 
               attack=False, env=False, getfile=False, postfile=False, temp_dir=None, postfile_path=None)
"""


@decorator.log_title(my_enum.Mode.normal)
def visit_slow(prefix: str, url: str, method: my_enum.Method, repeat_num: int, sleep: int, logger=None):
    node = my_node.requestNode(url, method=method)
    normal_run(prefix, request_list=[node], repeat_num=repeat_num, sleep=sleep, logger=logger)


@decorator.log_title(my_enum.Mode.attack_slow)
def visit_attack_slow(prefix: str, repeat_num: int, sleep: int, logger=None):
    nodelist = []
    for url in attack_url_list:
        node = my_node.requestNode(url)
        nodelist.append(node)
    normal_run(prefix, request_list=nodelist, repeat_num=repeat_num, sleep=sleep, logger=logger, attack=True)


@decorator.log_title(my_enum.Mode.getfile)
def get_file(prefix: str, get_size: int, repeat_num: int, sleep: int, logger=None):
    url = "/file?size=%s&unit=mb" % get_size
    node = my_node.requestNode(url)
    normal_run(prefix, request_list=[node], repeat_num=repeat_num, sleep=sleep, logger=logger, getfile=True)


@decorator.log_title(my_enum.Mode.postfile)
def post_file(prefix: str, post_size: int, repeat_num: int, sleep: int, logger=None):
    url = "/file?size=%s&unit=mb" % post_size
    postfile_path = os_validator.creat_postfile(post_size, "mb")
    node = my_node.requestNode(url)
    normal_run(prefix, request_list=[node], repeat_num=repeat_num, sleep=sleep, logger=logger, postfile=True, postfile_path=postfile_path)
    os_validator.delete_file(postfile_path)


@decorator.log_title(my_enum.Mode.env_slow)
def visit_env_slow(prefix: str, url: str, env_name: str, repeat_num: int, sleep: int, logger=None):
    temp_dir, nodelist = get_env_node(url, env_name, logger)
    normal_run(prefix, request_list=nodelist, repeat_num=repeat_num, sleep=sleep, logger=logger, env=True, temp_dir=temp_dir)
    os_validator.delete_dir(temp_dir)


@decorator.log_title(my_enum.Mode.getfile_env)
def get_file_env(prefix: str, env_name: str, get_size: int, repeat_num: int, sleep: int, logger=None):
    url = "/file?size=%s&unit=mb" % get_size
    temp_dir, nodelist = get_env_node(url, env_name, logger)
    normal_run(prefix, request_list=nodelist, repeat_num=repeat_num, sleep=sleep, logger=logger, env=True, getfile=True, temp_dir=temp_dir)
    os_validator.delete_dir(temp_dir)


@decorator.log_title(my_enum.Mode.postfile_env)
def post_file_env(prefix: str, env_name: str, post_size: int, repeat_num: int, sleep: int, logger=None):
    url = "/file?size=%s&unit=mb" % post_size
    postfile_path = os_validator.creat_postfile(post_size, "mb")
    temp_dir, nodelist = get_env_node(url, env_name, logger)
    normal_run(prefix, request_list=nodelist, repeat_num=repeat_num, sleep=sleep, logger=logger,
               env=True, postfile=True, temp_dir=temp_dir, postfile_path=postfile_path)
    os_validator.delete_dir(temp_dir)
    os_validator.delete_file(postfile_path)


"""
class requestNode:
    def __init__(self, url, para='', method=Method.GET, waf_ip=None, src_ip=None, agent=None, host=None, region=None, 
                 repeat_id=0)
                             
def threads_run(prefix, request_list=None, repeat_num=1, thread_num=5, logger=None, attack=False, env=False, temp_dir=None)
"""


@decorator.log_title(my_enum.Mode.fast)
def visit_fast(prefix: str, url: str, method: my_enum.Method, repeat_num: int, thread_num: int, logger=None):
    node = my_node.requestNode(url, method=method)
    threads_run(prefix, request_list=[node], repeat_num=repeat_num, thread_num=thread_num, logger=logger)


@decorator.log_title(my_enum.Mode.attack_fast)
def visit_attack_fast(prefix: str, repeat_num: int, thread_num: int, logger=None):
    nodelist = []
    for url in attack_url_list:
        node = my_node.requestNode(url)
        nodelist.append(node)
    threads_run(prefix, request_list=nodelist, repeat_num=repeat_num, thread_num=thread_num, logger=logger, attack=True)


@decorator.log_title(my_enum.Mode.env_fast)
def visit_env_fast(prefix: str, url: str, env_name: str, repeat_num: int, thread_num: int, logger=None):
    temp_dir, nodelist = get_env_node(url, env_name, logger)
    threads_run(prefix, request_list=nodelist, repeat_num=repeat_num, thread_num=thread_num, logger=logger, env=True, temp_dir=temp_dir)
    os_validator.delete_dir(temp_dir)


################## helper functions
def get_env_node(url: str, env_name: str, logger):
    temp_dir = os_validator.create_dir("cache/temp", repeat=True)
    ips, regions = info_getter.get_lb(env_name, logger)
    nodelist = []
    for ip_pos, ip in enumerate(ips):
        node = my_node.requestNode(url, waf_ip=ip, region=regions[int(ip_pos / 2)])
        nodelist.append(node)
    return temp_dir, nodelist
