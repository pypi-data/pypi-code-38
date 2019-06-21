import logging
import logging.handlers


def logs(file=None, mode='a', level=logging.DEBUG):

    logger = logging.getLogger(__name__)
    logger.setLevel(level=level)

    formatter = logging.Formatter('%(asctime)s - [line:%(lineno)d] %(filename)s - [%(levelname)s]: %(message)s')

    if file:
        handler = logging.FileHandler(file, mode)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def pro_logs(mode='a', level=logging.DEBUG):
    logger = logging.getLogger(__name__)
    logger.setLevel(level=level)

    formatter = logging.Formatter('%(asctime)s - [line:%(lineno)d] %(filename)s - [%(levelname)s]: %(message)s')

    handler = logging.handlers.HTTPHandler('localhost:5000', '/api/v1.0/logger', method='POST')
    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

if __name__ == '__main__':
    # logtest = logs('./logtest.log', 'w')
    # logtest.debug('fdsafasfsa')
    # logtest.info('abcadfa')
    # logtest.warning('ifjdsiafpasfapfdj')
    # logtest.error('fdsiafjasofjasdifojas')
    #
    # logtest2 = logs()
    # logtest2.debug('fadsfasfas')
    # logtest2.info('fsdiafjoasfoisdf')
    # logtest2.warning('fjsiadfjoasdjfiosa')
    # logtest2.error('ifjdsoafisadfjfjaisdfos')
    # try:
    #     a = 1 / 0
    # except Exception as e:
    #     logtest2.error(e)

    logtest3 = pro_logs()
    logtest3.info('adfadsf')
    logtest3.warning({'dfijdsa':'dfidsajo'})
    logtest3.error('adfadsf')
    logtest3.debug('adfadsf')