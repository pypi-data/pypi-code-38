'''

'''
import logging
import logging.handlers


class MyLogger:
    def __init__(self, host, url, name, level, message):
        self.level = level
        # 创建一个logger
        logger = logging.getLogger(name)

        # 设置handler
        # 创建一个log的处理器
        lh = logging.handlers.HTTPHandler(host, url)
        lh = logging.StreamHandler()
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # add formatter to ch
        lh.setFormatter(formatter)

        # 生成log
        if self.level == 'debug':
            # 设定logging的level，添加handler，生成log信息
            logger.setLevel(logging.DEBUG)
            logger.addHandler(lh)
            logger.debug(message)
        if self.level == 'info':
            logger.setLevel(logging.DEBUG)
            logger.addHandler(lh)
            logger.info(message)
        if self.level == 'warning':
            logger.setLevel(logging.DEBUG)
            logger.addHandler(lh)
            logger.warning(message)
        if self.level == 'error':
            logger.setLevel(logging.DEBUG)
            logger.addHandler(lh)
            logger.error(message)
        if self.level == 'critical':
            logger.setLevel(logging.DEBUG)
            logger.addHandler(lh)
            logger.critical(message)
        print('ok')
