import json
import sys


def get_lb(env_name: str, logger):
    with open("repo/lb_info.json", 'r') as f:
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


def get_host(prefix: str):
    if prefix.startswith('http://'):
        prefix = prefix[len('http://'):]
    if prefix.startswith('https://'):
        prefix = prefix[len('https://'):]
    if prefix.endswith('/'):
        prefix = prefix[:-1]
    return prefix
