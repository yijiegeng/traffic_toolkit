import copy
import queue
import time
from helper.logger_setter import info_handler, error_handler
from service.sender import requests_sender, curl_sender
from repo import my_enum, my_node


def processor(logger, prefix, work_queue,
              finish_queue=None, thread_name=None, sleep=0,
              attack=False, env=False, getfile=False, postfile=False,
              temp_dir=None, postfile_path=None):
    """
    class requestNode:
    def __init__(self, url, para='', method=Method.GET, waf_ip=None, src_ip=None, agent=None, host=None, region=None,
                     repeat_id=0):
    """
    qsize = work_queue.qsize()
    request = work_queue.get()

    ### required field
    url = request.url
    para = request.para
    method = request.method
    index = request.repeat_id

    ### optional field (use for header/log)
    waf_ip = request.waf_ip
    src_ip = request.src_ip
    agent = request.agent
    host = request.host
    region = request.region

    headers = {}
    if src_ip is not None:
        headers['X-Forwarded-For'] = src_ip
    if agent is not None:
        headers['User-Agent'] = agent
    if host is not None:
        headers['Host'] = host

    # special attack cases
    if url == "/lineComments":
        body = 'a=1 #'
    elif url == "/jsVariable":
        body = 'id=hello";document.body.innerHTML="ddddd"//'
    else:
        body = None

    response_size = None
    request_size = None
    try:
        # used for normal request
        if env is False:
            if getfile:
                code, waf_ip, response_size, _ = requests_sender(
                    logger, prefix, url, method=my_enum.Method.GET, para=para, headers=headers, body=body)
            elif postfile:
                code, waf_ip, response_size, request_size = requests_sender(
                    logger, prefix, url, method=my_enum.Method.POST, para=para, headers=headers, body=body,
                    postfile_path=postfile_path)
            else:
                code, waf_ip, _, _ = requests_sender(
                    logger, prefix, url, method=method, para=para, headers=headers, body=body)

        # used for curl request
        else:
            if getfile:
                code, waf_ip, response_size, _ = curl_sender(
                    logger, temp_dir, prefix, url, waf_ip, thread_name=thread_name)
            elif postfile:
                code, waf_ip, response_size, request_size = curl_sender(
                    logger, temp_dir, prefix, url, waf_ip, thread_name=thread_name, postfile_path=postfile_path)
            else:
                code, waf_ip, _, _ = curl_sender(
                    logger, temp_dir, prefix, url, waf_ip, thread_name=thread_name)

        info_log = info_handler(url, code, index, sleep,
                                qsize=qsize,
                                thread_name=thread_name,
                                method=method,
                                region=region,
                                waf_ip=waf_ip,
                                response_size=response_size,
                                request_size=request_size)


        logger.info(info_log)
    except Exception as e:
        logger.warning(error_handler(url, e, index, sleep,
                                     qsize=qsize,
                                     thread_name=thread_name,
                                     method=method,
                                     region=region))

    finally:
        time.sleep(sleep)
        if finish_queue is not None:
            finish_queue.put(True)


def creat_msg_queue(repeat_num, request_list):
    qsize = repeat_num * (len(request_list) if request_list is not None else 1)
    work_queue = queue.Queue(qsize)  # set queue size
    finish_queue = queue.Queue(qsize)
    for i in range(repeat_num):
        if request_list is None or len(request_list) == 0:
            work_queue.put(my_node.requestNode(repeat_id=i, url="/"))  # default url = "/"
        else:
            temp = copy.deepcopy(request_list)
            for node in temp:  # put the request_node to queue
                if isinstance(node, str): node = my_node.requestNode(repeat_id=i,
                                                                     url=node)  # in case node is a str (url)
                node.repeat_id = i
                work_queue.put(node)
    return work_queue, finish_queue
