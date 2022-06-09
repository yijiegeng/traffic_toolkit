
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
