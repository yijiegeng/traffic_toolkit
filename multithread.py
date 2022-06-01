import copy
import threading
import time
import queue
import urllib3
from alive_progress import alive_bar
from logger_setter import set_logger, info_handler, error_handler
from send_helper import requests_sender, curl_sender
from my_enum import Method

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class requestNode:
    def __init__(self, url='/', para='', method=Method.GET, repeat_id=0,
                 src_ip=None, agent=None, host=None, region=None, env_mode=False):
        self.url = url
        self.para = para
        self.method = method
        self.repeat_id = repeat_id
        self.src_ip = src_ip
        self.agent = agent
        self.host = host
        self.region = region
        self.env_mode = env_mode


def work(thread_name, prefix, work_queue, finish_queue, initial_size, logger, temp_dir):
    if thread_name == "Thread-0":
        with alive_bar(initial_size, manual=True) as bar:
            while True:
                curr_size = finish_queue.qsize()
                bar(curr_size / initial_size)
                if finish_queue.qsize() == initial_size:
                    bar(1)
                    return
    else:
        while True:
            if work_queue.empty():
                # print("Exiting ", thread_name)
                return
            else:
                crawler(temp_dir, thread_name, prefix, work_queue, finish_queue, logger)


def crawler(temp_dir, thread_name, prefix, work_queue, finish_queue, logger):
    request = work_queue.get()
    ### required field
    url = request.url
    para = request.para
    method = request.method
    index = request.repeat_id
    ### optional field (use for header/logger)
    src_ip = request.src_ip
    agent = request.agent
    host = request.host
    region = request.region
    env_mode = request.env_mode

    headers = {}
    # special case
    if url == "/bot":
        headers['User-Agent'] = 'Cgichk'
    elif url == "/rootkit.php":
        headers['X_File'] = 'data.txt'

    if src_ip is not None:
        headers['X-Forwarded-For'] = src_ip
    if agent is not None:
        headers['User-Agent'] = agent
    if host is not None:
        headers['Host'] = host

    try:
        if not env_mode:    # used for normal request
            code, waf_ip, _, _ = requests_sender(prefix, url,
                                                 method=method,
                                                 para=para,
                                                 headers=headers)
        else:               # used for curl request
            code, waf_ip, _, _ = curl_sender(temp_dir, prefix, url, src_ip,
                                             filename=thread_name)

        logger.info(info_handler(url, code, index,
                                 qsize=work_queue.qsize(),
                                 thread_name=thread_name,
                                 method=method,
                                 region=region,
                                 waf_ip=waf_ip))
    except Exception as e:
        logger.error(error_handler(url, e, index,
                                   qsize=work_queue.qsize(),
                                   thread_name=thread_name,
                                   method=method,
                                   region=region))
    finally:
        finish_queue.put(True)


def threads_run(prefix, request_list=[], repeat_num=1, thread_num=10, logger=None, temp_dir=None):
    if logger is None: logger = set_logger("multithread")
    start = time.time()

    # create message queue
    work_queue = queue.Queue(1000)  # set queue size
    finish_queue = queue.Queue(1000)
    for i in range(repeat_num):
        if len(request_list) == 0:
            work_queue.put(requestNode(repeat_id=i))  # default url = "/"
        else:
            temp = copy.deepcopy(request_list)
            for node in temp:  # put the request_node to queue
                if isinstance(node, str): node = requestNode(url=node)  # in case node is a str (url)
                node.repeat_id = i
                work_queue.put(node)
    initial_size = work_queue.qsize()

    # create threads list
    thread_list = []  # create thread_name
    for i in range(thread_num):
        thread_list.append('Thread-' + str(i))
    threads = []  # thread pool
    for tName in thread_list:  # create new thread
        thread = threading.Thread(target=work, args=(tName, prefix, work_queue, finish_queue,
                                                     initial_size, logger, temp_dir))
        threads.append(thread)

    for t in threads:  # waiting for all threads start
        t.start()
    for t in threads:  # waiting for all threads done
        t.join()

    # end = time.time()
    # print('Total time：', end - start)
    print('Exiting Main Thread')


if __name__ == "__main__":
    threads_run("https://52.78.82.9:8080", repeat_num=20, thread_num=5)
