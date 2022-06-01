import os
import shutil
import subprocess
import requests
from my_enum import Method


def requests_sender(prefix, url, para="", method=Method.GET, headers={}, postfile_path=None):
    files = None if postfile_path is None else {'file': open(postfile_path, 'rb')}
    try:
        if method == Method.GET:
            resp = requests.get(prefix + url + para, headers=headers, verify=False, timeout=20)
        elif method == Method.POST:
            resp = requests.post(prefix + url + para, headers=headers, verify=False, files=files)
        elif method == Method.PUT:
            resp = requests.put(prefix + url + para, headers=headers, verify=False, timeout=20)
        elif method == Method.DELETE:
            resp = requests.delete(prefix + url + para, headers=headers, verify=False, timeout=20)
        elif method == Method.PATCH:
            resp = requests.patch(prefix + url + para, headers=headers, verify=False, timeout=20)
        elif method == Method.OPTIONS:
            resp = requests.options(prefix + url + para, headers=headers, verify=False, timeout=20)
        else:
            raise Exception("Invalid method!", method)
    except Exception as e:
        raise e

    headers = resp.headers
    code = resp.status_code
    waf_ip = headers["WAF-ip"] if "WAF-ip" in headers else None
    response_size = headers["Content-Length"] if "Content-Length" in headers else len(resp.content)
    request_size = headers["Request-Size"] if "Request-Size" in headers else 0

    return code, waf_ip, int(response_size), int(request_size)


def curl_sender(prefix, url, ip, filename=None, postfile_path=None):
    host = get_host(prefix)
    header_file = "temp/header.txt"
    error_file = "temp/error.txt"
    output_file = "temp/output.txt"
    if filename is not None:
        output_file = "temp/%s_output.txt" % filename
        header_file = "temp/%s_header.txt" % filename
        error_file = "temp/%s_error.txt" % filename

    if postfile_path is None:
        # GET
        subprocess.call('curl "https://%s" --resolve %s:443:%s --insecure --silent --show-error --connect-timeout 10 '
                        '--output %s --dump-header %s --stderr %s'
                        % (host + url, host, ip, output_file, header_file, error_file), shell=True)
    else:
        # POST
        subprocess.call('curl "https://%s" --resolve %s:443:%s --insecure --silent --show-error --connect-timeout 10 '
                        '--output %s --dump-header %s --stderr %s -F "file=@%s"'
                        % (host + url, host, ip, output_file, header_file, error_file, postfile_path), shell=True)

    (code, waf_ip, response_size, request_size, error, console_emsg) = pars_output(header_file, error_file)
    if error is not None:
        raise error
    if console_emsg is not None:
        raise Exception(console_emsg)
    if response_size is None:
        response_size = os.path.getsize(output_file)
    if request_size is None:
        request_size = 0

    return code, waf_ip, int(response_size), int(request_size)


def pars_output(header_file, error_file):
    code = None
    ip = None
    response_size = None
    request_size = None
    error = None
    console_emsg = None
    try:
        with open(error_file, "r") as f:
            # fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            lines = f.readlines()
            if len(lines) > 0:
                console_emsg = lines[0].strip()
    except Exception as e:
        error = e
    if not error and not console_emsg:
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
            error = e

    return code, ip, response_size, request_size, error, console_emsg


def get_host(prefix):
    if prefix.startswith('http://'):
        prefix = prefix[len('http://'):]
    if prefix.startswith('https://'):
        prefix = prefix[len('https://'):]
    if prefix.endswith('/'):
        prefix = prefix[:-1]
    return prefix


def create_temp():
    if not os.path.isdir("temp"):
        os.makedirs("temp")


def delete_temp():
    dir_path = "temp"
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        raise e
