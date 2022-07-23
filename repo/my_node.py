from repo import my_enum


class requestNode:
    def __init__(self, url, para='', method=my_enum.Method.GET, waf_ip=None, src_ip=None, agent=None, host=None, region=None,
                 repeat_id=0):
        self.url = url
        self.para = para
        self.method = method
        self.waf_ip = waf_ip
        self.src_ip = src_ip
        self.agent = agent
        self.host = host
        self.region = region
        self.repeat_id = repeat_id
