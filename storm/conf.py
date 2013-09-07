import os
from os.path import join

import yaml
from logbook import Logger

logger = Logger('conf')


def get_global():
    logger.info('Loading global config')
    xdg = os.getenv('XDG_CONFIG_DIRS', '/etc/xdg')
    filename = join(xdg, 'storm', 'config.yml')
    return yaml.load(open(filename))


def get_local():
    logger.info('Loading local config')
    xdg = os.getenv('XDG_CONFIG_HOME', join(os.getenv('HOME'), '.config'))
    local = join(xdg, 'storm', 'config.yml')

    try:
        return yaml.load(open(local))
    except Exception:
        logger.warning('No local configuration file found at: {0}', local)
        return {}


def load():
    global_yaml = get_global()
    local_yaml = get_local()

    # Merge the two by overwriting the data from local
    global_yaml.update(local_yaml)
    return global_yaml

CONFIG = load()
