import logging
from kube_hunter.conf.parser import arg_parse


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
    def get_conf(self):
        config = arg_parse()

        log_level = getattr(logging, config.log.upper(), logging.INFO)
        if config.log.lower() != "none":
            logging.basicConfig(level=log_level, format='%(message)s', datefmt='%H:%M:%S')

        self.__init_conf(config)
        return config

    def __init_conf(self, config):
        for attr in config:
            setattr(self, attr, config[attr])
