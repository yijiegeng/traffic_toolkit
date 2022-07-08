import os
import subprocess
import requests
import urllib3
from repo.my_enum import Method
from helper import os_validator, info_getter
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def requests_sender(logger, prefix, url, para="", method=Method.GET, headers=None, body=None, postfile_path=None):
    files = None if postfile_path is None else {'file': open(postfile_path, 'rb')}
    try:
        if method == Method.GET:
            resp = requests.get(prefix + url + para, headers=headers, data=body, verify=False, timeout=20)
        elif method == Method.POST:
            resp = requests.post(prefix + url + para, headers=headers, data=body, verify=False, files=files)
        elif method == Method.PUT:
            resp = requests.put(prefix + url + para, headers=headers, data=body, verify=False, timeout=20)
        elif method == Method.DELETE:
            resp = requests.delete(prefix + url + para, headers=headers, data=body, verify=False, timeout=20)
        elif method == Method.PATCH:
            resp = requests.patch(prefix + url + para, headers=headers, data=body, verify=False, timeout=20)
        elif method == Method.OPTIONS:
            resp = requests.options(prefix + url + para, headers=headers, data=body, verify=False, timeout=20)
        else:
            raise Exception("Invalid method!", method)
    except Exception as e:
        logger.error("Requests Running Failed: %s" % e)
        raise

    headers = resp.headers
    code = resp.status_code
    waf_ip = headers["WAF-ip"] if "WAF-ip" in headers else None
    response_size = headers["Content-Length"] if "Content-Length" in headers else len(resp.content)
    request_size = headers["Request-Size"] if "Request-Size" in headers else 0

    return code, waf_ip, int(response_size), int(request_size)


def curl_sender(logger, temp_dir, prefix, url, ip, thread_name=None, postfile_path=None):
    host = info_getter.get_host(prefix)
    port = ":443" if ":" not in host else ""

    if thread_name is not None:
        temp_dir = os_validator.create_dir(temp_dir + thread_name)

    header_file = temp_dir + "header.txt"
    error_file = temp_dir + "error.txt"
    output_file = temp_dir + "output.txt"

    try:
        if postfile_path is None:
            # GET
            subprocess.call('curl "https://%s" --resolve %s:%s --insecure --silent --show-error --connect-timeout 5'
                            ' --output %s --dump-header %s --stderr %s'
                            % (host + url, host + port, ip, output_file, header_file, error_file), shell=True)
        else:
            # POST
            subprocess.call('curl "https://%s" --resolve %s:%s --insecure --silent --show-error --connect-timeout 10'
                            ' --output %s --dump-header %s --stderr %s -F "file=@%s"'
                            % (host + url, host + port, ip, output_file, header_file, error_file, postfile_path), shell=True)

    except Exception as e:
        logger.error("CURL Running Failed: %s" % e)
        raise

    (code, waf_ip, response_size, request_size, console_emsg) = pars_output(logger, header_file, error_file)

    if console_emsg is not None:
        raise Exception(console_emsg)
    if response_size is None:
        response_size = os.path.getsize(output_file)
    if request_size is None:
        request_size = 0

    return code, waf_ip, int(response_size), int(request_size)


def pars_output(logger, header_file, error_file):
    code = None
    ip = None
    response_size = None
    request_size = None
    console_emsg = None
    try:
        with open(error_file, "r") as f:
            # fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            lines = f.readlines()
            if len(lines) > 0:
                console_emsg = lines[0].strip()
    except Exception as e:
        logger.error("CURL [error_file] Parse Failed: %s" % e)
        raise

    if not console_emsg:
        try:
            with open(header_file, "r") as f:
                # fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                lines = f.readlines()
                first_line = lines[0]
                code = first_line.split(" ")[1]
                other = lines[1:]
                for line in other:
                    if line.startswith("Content-Length"):
                        response_size = line[len("Content-Length: "):].strip()
                    elif line.startswith("Request-Size"):
                        request_size = line[len("Request-Size: "):].strip()
                    elif line.startswith("WAF-ip"):
                        ip = line[len("WAF-ip: "):].strip()
                        break
        except Exception as e:
            logger.error("CURL [header_file] Parse Failed: %s" % e)
            raise

    return code, ip, response_size, request_size, console_emsg
