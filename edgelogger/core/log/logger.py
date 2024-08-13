import logging
from logging import handlers

class PseudoLogger(object):
    def debug(self, object):
        pass

    def info(self, object):
        pass

    def error(self, object):
        pass

    def warning(self, object):
        pass

    def warn(self, object):
        pass

    def critical(self, object):
        pass

class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='info', when='D', backCount=3, fmt='%(asctime)s - %(pathname)s:%(lineno)d] - %(levelname)s: %(message)s'):
        if filename != "":
            self.logger = logging.getLogger(filename)
            format_str = logging.Formatter(fmt)
            self.logger.setLevel(self.level_relations.get(level))

            sh = logging.StreamHandler()
            sh.setFormatter(format_str)

            th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount, encoding='utf-8')
            th.setFormatter(format_str)

            self.logger.addHandler(sh) 
            self.logger.addHandler(th)
        else:
            self.logger = PseudoLogger()

# log = Logger("debug.log", level="debug", fmt='%(asctime)s-[%(filename)s:%(funcName)s:%(lineno)d]-%(levelname)s:%(message)s')
log = Logger("", level="debug")