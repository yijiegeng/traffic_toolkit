from optparse import OptionParser
from my_enum import Method, enum_standardize
import executor


def main():
    usage = "usage: %prog [options] arg (refer %prog --help)"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--domain", action="store", dest="domain",
                      help="Domain name (required!)")
    parser.add_option("-u", "--url", action="store", dest="url", default="/",
                      help="URL")
    parser.add_option("-m", "--method", action="store", dest="method",
                      help="input is requests method: [get, post, put, delete, patch, options]")
    parser.add_option("-r", "--repeat", action="store", dest="repeat", type="int", default=1,
                      help="input is repeat_num")
    parser.add_option("-s", "--sleep", action="store", dest="sleep", type="float",
                      help="input is sleep seconds between each repeat_round")
    parser.add_option("-f", "--fast", action="store", dest="fast", type="int",
                      help="Fast mode: Using multi-threads to run, input is threads_num")
    parser.add_option("-a", "--attack", action="store_true", dest="attack",
                      help="attack mode: Send attack requests. (note: send 13 attacks/time)")
    parser.add_option("-e", "--env", action="store", dest="env",
                      help="env mode: which environment region you wanna test? traffic will go through different region")
    parser.add_option("-g", "--gfile", action="store", dest="get_size", type="int",
                      help="send_file mode: send a file, unit is MB")
    parser.add_option("-p", "--pfile", action="store", dest="post_size", type="int",
                      help="post_file mode: send a file and receive a file, unit is MB")

    (options, args) = parser.parse_args()

    # validation for input
    if options.domain is None:
        parser.error("Domain is required!")
    conflict = check_input(options)
    if len(conflict) > 0:
        parser.error('[' + ",".join(conflict) + "] are mutually exclusive! Please check <--help> for usage")

    method = options.method
    try:
        method = enum_standardize(options.method)
    except Exception as e:
        parser.error(e)

    execute(options, method)


def execute(options, method):
    domain = domain_standardize(options.domain)
    url = url_standardize(options.url)
    repeat_num = options.repeat
    sleep = options.sleep
    thread_num = options.fast
    env_name = options.env
    attack = options.attack
    get_size = options.get_size
    post_size = options.post_size

    if post_size is not None: method = Method.POST
    if sleep is None: sleep = 0
    hint = ">>>>>>>> %s [%s]\n>>>>>>>> repeat [%s] times" % (domain + url, method.value, repeat_num)
    if sleep != 0:
        hint += ", sleep [%s] seconds" % sleep
    if thread_num is not None:
        hint += ", with [%s] threads" % thread_num
    if env_name is not None:
        hint += ", runs on [%s] env regions" % env_name
    if attack:
        hint += " --> sending 13 types attack (make sure SBD is enabled on FWB cloud)"
    if get_size is not None:
        hint += " --> getting [%s] mb file" % get_size
    if post_size is not None:
        hint += " --> sending and receiving [%s] mb files" % post_size

    s = input(hint + "\n[y/n] (press any key for yes):")
    if s == "n":
        print("Modify and run again.")
        return

    ####### attack-slow mod #######
    if attack and (thread_num is None):
        executor.visit_attack_slow(domain, repeat_num=repeat_num, sleep=sleep)

    ####### attack-fast mod #######
    elif attack and (thread_num is not None):
        executor.visit_attack_fast(domain, repeat_num=repeat_num, thread_num=thread_num)

    ####### env-slow mod #######
    elif (env_name is not None) and (thread_num is None) and (get_size is None) and (post_size is None):
        executor.visit_env_slow(domain, url, env_name, repeat_num=repeat_num, sleep=sleep)

    ####### env-fast mod #######
    elif (env_name is not None) and (thread_num is not None):
        executor.visit_env_fast(domain, url, env_name, repeat_num=repeat_num, thread_num=thread_num)

    ####### get_file mod #######
    elif (get_size is not None) and (env_name is None):
        executor.get_file(domain, get_size=get_size, repeat_num=repeat_num, sleep=sleep)

    ####### post_file mod #######
    elif (post_size is not None) and (env_name is None):
        executor.post_file(domain, post_size=post_size, repeat_num=repeat_num, sleep=sleep)

    ####### env-get_file mod #######
    elif (get_size is not None) and (env_name is not None):
        executor.get_file_env(domain, env_name, get_size=get_size, repeat_num=repeat_num, sleep=sleep)

    ####### env-post_file mod #######
    elif (post_size is not None) and (env_name is not None):
        executor.post_file_env(domain, env_name, post_size=post_size, repeat_num=repeat_num, sleep=sleep)

    ####### fast mod #######
    elif options.fast is not None:
        executor.visit_fast(domain, url, method=method, repeat_num=repeat_num, thread_num=thread_num)

    ####### normal mod #######
    else:
        executor.visit_slow(domain, url, method=method, repeat_num=repeat_num, sleep=sleep)


def check_input(options):
    conflict_map = {'-a': {'-e', '-g', '-p', '-m'},
                    '-g': {'-a', '-f', '-p', '-m'},
                    '-p': {'-a', '-f', '-g', '-m'},
                    '-m': {'-a', '-g', '-p', '-e'},
                    '-f': {'-s', '-g', '-p'},
                    '-e': {'-a', '-m'},
                    '-s': {'-f'}
                    }

    input_set = set()
    if options.attack:
        input_set.add("-a")
    if options.get_size is not None:
        input_set.add("-g")
    if options.post_size is not None:
        input_set.add("-p")
    if options.method is not None:
        input_set.add("-m")
    if options.fast is not None:
        input_set.add("-f")
    if options.env is not None:
        input_set.add("-e")
    if options.sleep is not None:
        input_set.add("-s")

    conflict = set()
    for para in input_set:
        conflict_candi = input_set & conflict_map[para]
        if len(conflict_candi) > 0:
            conflict.add(para)
            conflict = conflict | conflict_candi
    return conflict


def domain_standardize(s):  # add 'https://'
    s = s.strip()
    if not (s.startswith('http://') or s.startswith('https://')):
        s = 'https://' + s
    if s.endswith('/'):
        s = s[:-1]
    return s


def url_standardize(s):  # add '/'
    s = s.strip()
    if not s.startswith('/'):
        s = '/' + s
    return s


if __name__ == "__main__":
    main()
