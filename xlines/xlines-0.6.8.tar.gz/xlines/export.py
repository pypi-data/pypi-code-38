import sys
import json
import inspect
from pygments import highlight, lexers, formatters
from xlines import logger


def export_json_object(dict_obj, filename=None, logging=True):
    """
    Summary:
        exports object to block filesystem object

    Args:
        :dict_obj (dict): dictionary object
        :filename (str):  name of file to be exported (optional)

    Returns:
        True | False Boolean export status

    """
    def is_tty():
        """
        Summary:
            Determines if output is displayed to the screen or redirected
        Returns:
            True if tty terminal | False is redirected, TYPE: bool
        """
        return sys.stdout.isatty()

    try:

        if filename:

            try:

                with open(filename, 'w') as handle:
                    handle.write(json.dumps(dict_obj, indent=4, sort_keys=True))
                    logger.info(
                        '%s: Wrote %s to local filesystem location' %
                        (inspect.stack()[0][3], filename))

                handle.close()

            except TypeError as e:
                logger.warning(
                    '%s: object in dict not serializable: %s' %
                    (inspect.stack()[0][3], str(e)))

        elif is_tty():

            json_str = json.dumps(dict_obj, indent=4, sort_keys=True)

            print(
                highlight(
                    json_str,
                    lexers.JsonLexer(),
                    formatters.TerminalFormatter()
                ).strip()
            )
            if logging:
                logger.info('%s: successful export to stdout' % inspect.stack()[0][3])
            return True

        else:
            # print output, but not to stdout; possibly commandline redirect
            print(json.dumps(dict_obj, indent=4, sort_keys=True))

    except OSError as e:
        logger.critical(
            '%s: export_file_object: error writing to %s to filesystem. Error: %s' %
            (inspect.stack()[0][3], filename, str(e)))
        return False
    if logging:
        logger.info('export_file_object: successful export to %s' % filename)
    return True
