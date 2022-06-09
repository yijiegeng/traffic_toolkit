import os
import re
import shutil


def creat_postfile(size, unit):
    path = create_dir("cache")
    fullpath = path + "postfile.log"
    fullpath = check_duplicate(fullpath)
    size = int(size)
    with open(fullpath, "w") as f:
        if str.lower(unit) == 'kb':
            size *= 1024 - 1
        elif str.lower(unit) == 'mb':
            size *= 1024 * 1024 - 1
        f.seek(size)
        f.write('end')
    return fullpath


def create_dir(rootpath: str, repeat=False):
    if rootpath.startswith("/"):
        rootpath = rootpath[1:]
    if rootpath.endswith("/"):
        rootpath = rootpath[:-1]

    if not repeat:
        path = rootpath
        if not os.path.exists(path):
            os.makedirs(path)
    else:
        path = check_duplicate(rootpath)
        os.makedirs(path)
    return path + "/"


def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)


def delete_dir(dir_name):
    if not os.path.exists(dir_name):
        print(dir_name, "not exist!")
        return
    try:
        shutil.rmtree(dir_name)
    except OSError as e:
        raise e


def get_logpath(func_name):
    path = create_dir("log")
    logpath = path + func_name + ".log"
    return check_duplicate(logpath)


def check_duplicate(path: str):
    filetype = ""
    if "." in path:
        index = path.index(".")
        filetype = path[index:]
        path = path[:index]

    prefix = path
    suffix = 1
    if "_" in path:
        str_pattern = re.compile(r".*_[0-9]+$")
        if str_pattern.match(path):
            index = path.rindex("_")
            suffix = int(path[(index + 1):])
            prefix = path[:index]

    path = prefix + "_" + str(suffix) + filetype
    while os.path.exists(path):
        suffix += 1
        path = prefix + "_" + str(suffix) + filetype

    return path
