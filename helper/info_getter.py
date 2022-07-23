import json
import sys


def get_lb(env_name: str, region: str, logger=None):
    with open("repo/lb_info.json", 'r') as f:
        try:
            data = json.load(f)
            if env_name not in data:
                print("[%s] env not found!" % env_name)
                sys.exit(0)
            if region is not None and region not in data[env_name]["lb-region"]:
                print("[%s] region not found!" % region)
                sys.exit(0)
        except json.decoder.JSONDecodeError as e:
            if logger is not None:
                logger.error("lb_info.json loading failed!", e)
            else:
                print("lb_info.json loading failed!", e)
            sys.exit(0)

        ips = data[env_name]["lb-ip"]
        regions = data[env_name]["lb-region"]
        if region is not None:
            index = regions.index(region)
            ips = ips[index*2:index*2+2]
            regions = [region]
    return ips, regions


def get_host(prefix: str):
    if prefix.startswith('http://'):
        prefix = prefix[len('http://'):]
    if prefix.startswith('https://'):
        prefix = prefix[len('https://'):]
    if prefix.endswith('/'):
        prefix = prefix[:-1]
    return prefix
