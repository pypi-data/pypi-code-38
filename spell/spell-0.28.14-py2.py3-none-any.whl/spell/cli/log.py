import logging
import sys
import click

logger_name = "spell"

logger = logging.getLogger(logger_name)


class ColorFormatter(logging.Formatter):
    colors = {
        logging.ERROR: dict(fg='red'),
        logging.CRITICAL: dict(fg='red'),
        logging.DEBUG: dict(fg='blue'),
        logging.WARNING: dict(fg='yellow'),
        logging.INFO: dict(fg='green')
    }

    def format(self, record):
        if not record.exc_info:
            if record.levelno in self.colors:
                raw_prefix = '{}: '.format(logging.getLevelName(record.levelno))
                prefix = click.style(raw_prefix, **self.colors[record.levelno])
                msg = record.msg
                text_type = unicode if (sys.version_info[0] == 2) else str # NOQA
                if not (sys.version_info[0] == 2) and isinstance(msg, bytes):
                    msg = msg.decode(sys.getfilesystemencoding(),
                                     'replace')
                elif not isinstance(msg, (text_type, bytes)):
                    msg = str(msg)
                msg = click.wrap_text(msg)

                # format messages with "level: message" and add a tab to
                # subsequent lines. For example:
                # `This is a
                # multi-line
                # message`
                # ->
                # level: This is a
                #        multi-line
                #        message
                record.msg = '\n'.join(prefix + x if i == 0 else " "*len(raw_prefix) + x
                                       for i, x in enumerate(msg.splitlines()))

        return logging.Formatter.format(self, record)


class ClickHandler(logging.Handler):

    def emit(self, record):
        try:
            msg = self.format(record)
            is_error = record.levelno in (logging.WARNING, logging.ERROR,
                                          logging.CRITICAL)
            click.echo(msg, err=is_error)
        # raise these exceptions up above
        except (KeyboardInterrupt, SystemExit):
            raise
        # defer to handleError for other exceptions encountered during logging
        except Exception:
            self.handleError(record)


def configure_logger(input_logger, level=logging.WARNING):
    handler = ClickHandler()
    handler.formatter = ColorFormatter()
    input_logger.handlers = [handler]
    input_logger.setLevel(level)
