import os
import re

import yaml


class Redis:
    def __init__(self, data: dict):
        self.host = data['host']
        self.port = data['port']
        self.db = data['db']
        self.ttl = data['ttl']
        self.password = data['password']


class Config:
    def __init__(self, data: dict):
        self.redis = Redis(data['redis'])


def parse(filepath):
    pattern = re.compile('^"?\\$\\{([^}^{]+)\\}"?$')

    def _path_constructor(loader, node):
        value = node.value
        match = pattern.match(value)
        env_var = match.group().strip('"${}')
        return os.environ.get(env_var) + value[match.end():]

    yaml.add_implicit_resolver('env', pattern, None, yaml.SafeLoader)
    yaml.add_constructor('env', _path_constructor, yaml.SafeLoader)

    with open(filepath, "r") as f:
        cfg = yaml.load(f, Loader=yaml.SafeLoader)
    return Config(cfg)
