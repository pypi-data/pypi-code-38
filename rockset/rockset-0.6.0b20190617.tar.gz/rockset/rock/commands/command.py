import json
import logging
import sys
import texttable
import yaml

from docopt import docopt
from http.client import HTTPConnection
from rockset.credentials import Credentials
from rockset.exception import (
    AuthError, HTTPError, InputError, LimitReached, NotYetImplemented,
    RequestTimeout, ResourceSuspendedError, ServerError, TransientServerError
)


class Command(object):
    def _parse_yaml_file(self, fn, upload=False):
        try:
            fh = open(fn, 'r')
            resources = self._parse_yaml_filehandle(fh, upload)
        except (IOError, OSError) as e:
            raise ValueError('cannot open YAML file {}'.format(fn))
        except ValueError as e:
            raise ValueError('cannot parse YAML file {}'.format(fn))
        finally:
            fh.close()
        return resources

    def _parse_yaml_filehandle(self, fh, upload):
        # split yaml file at '---' to support multiple resource definitions
        sections = []
        lines = []
        for line in fh:
            if line.rstrip() == '---':
                sections.append(lines)
                lines = []
                continue
            lines.append(line)
        if len(lines) > 0:
            sections.append(lines)

        resources = []
        for section in sections:
            rlist = yaml.load(''.join(section))
            if not isinstance(rlist, list):
                rlist = [rlist]
            for ro in rlist:
                if upload:
                    if 'collection' not in ro:
                        raise ValueError(
                                '"collection" is not defined for files '
                                'entry #{}'.format(len(resources))
                        )
                else:
                    if 'name' not in ro:
                        raise ValueError(
                            '"name" is not defined for resource '
                            'entry #{}'.format(len(resources))
                        )
                    if 'type' not in ro:
                        raise ValueError(
                            '"type" is not defined for resource '
                            'entry #{} name={}'.format(len(resources), ro['name'])
                        )
                resources.append(ro)
        return resources

    def __init__(self, *args, **kwargs):
        # set defaults
        self.profile = None
        self.batch_items = None
        self.verbose = 0
        self.logger = logging.getLogger(__name__)

        # override with input
        self.setattrs(*args, **kwargs)

        # initialize loggers
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s %(name)s %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
        )

        log_level = logging.CRITICAL
        if self.verbose >= 1:
            log_level = logging.WARNING
        if self.verbose >= 2:
            log_level = logging.INFO
        if self.verbose >= 3:
            log_level = logging.DEBUG
            HTTPConnection.debuglevel = 1
        for module in ['rockset', 'requests.packages.urllib3']:
            logger = logging.getLogger(module)
            logger.addHandler(handler)
            logger.setLevel(log_level)
            logger.propagate = True
            self.logger.debug(vars(logger))

        # log some info messages
        self.logger.info('command attrs: {}'.format(vars(self)))

    def setattrs(self, *args, **kwargs):
        for key in kwargs:
            attrkey = key
            if key[:2] == '--':
                attrkey = key[2:]
            elif key[:1] == '-':
                attrkey = key[1:]
            elif key[:1] == '<' and key[-1:] == '>':
                attrkey = key[1:-1]
            setattr(self, attrkey, kwargs[key])

    def set_batch_items(self, field, values):
        self.batch_items = {field: values}

    def get_batch_items(self):
        return self.batch_items

    def iter_batch_items(self):
        if self.batch_items is None:
            return
        field, values = self.batch_items.popitem()
        for v in values:
            yield (field, v)

    def _apicall(self, method, *args, **kwargs):
        self.logger.info('calling %s()' % method)
        self.logger.info('  with args: %s' % str(args))
        self.logger.info('  with kwargs: %s' % str(kwargs))
        result = self.client._apicall(method, *args, **kwargs)
        self.logger.info('received result: %s' % str(result))
        return result

    def parse_args(self, args):
        return dict(docopt(self.usage(), argv=args))

    def validate_args(self, pargs):
        # TODO (veeve): use schema module for validation
        return (pargs is not None)

    def main(self, args):
        # parse input args
        parsed_args = self.parse_args(args)

        # validate input args, some args are not compatible with others
        if not self.validate_args(parsed_args):
            raise SystemExit(self.usage().strip())

        # all is well, set command args to object
        assert (type(parsed_args) == dict)
        self.setattrs(**parsed_args)

        # run through all resources in batch or solo mode
        if self.get_batch_items() is not None:
            return self.main_batch_go()

        # regular mode; go
        return self.main_go()

    def main_batch_go(self):
        # accummulate exceptions in batch mode, don't bail in the middle
        ret = 0
        exceptions = []
        for f, v in self.iter_batch_items():
            try:
                setattr(self, f, v)
                ret += self.main_go()
            except AssertionError as e:
                # unless it is a test failure
                raise
            except SystemExit as e:
                # unless it is a test failure
                raise
            except Exception as e:
                self.logger.exception(e)
                ret = 1
                exceptions.append(e)
                if self.verbose:
                    raise
        return ret

    def main_go(self, *args, **kwargs):
        try:
            r = self.go(*args, **kwargs)
            if type(r) == int:
                ret = r
            elif type(r) == tuple:
                (ret, result) = r
                self.print_result(result)
            else:
                raise RuntimeError(
                    'unexpected command return type {}'.format(type(r))
                )

        except AuthError as e:
            self.logger.error('Error: {}'.format(str(e)))
            self.logger.exception(e)
            self.eprint(
                0, 'Hint: Use "rock configure" to update your '
                'credentials.'
            )
            ret = 126
            if self.verbose:
                raise
        except (
            HTTPError, InputError, LimitReached, NotImplementedError,
            NotYetImplemented, RequestTimeout, ResourceSuspendedError,
            ServerError, TransientServerError
        ) as e:
            self.logger.error('Error: {} {}'.format(type(e).__name__, str(e)))
            self.logger.exception(e)
            self.eprint(0, 'Error: {}'.format(str(e)))
            ret = 1
            if self.verbose:
                raise
        except Exception as e:
            self.logger.error('Unhandled exception: {}'.format(str(e)))
            self.logger.exception(e)
            self.eprint(0, 'Error: {} {}'.format(type(e).__name__, str(e)))
            ret = 1
            if self.verbose:
                raise
        return ret

    def go(self):
        raise NotImplementedError(
            'command "{}" not yet implemented'.format(self.command)
        )

    def require_creds(self):
        creds = Credentials()
        if self.profile is None:
            self.profile = creds.active_profile()
        profile = creds.get(self.profile)
        if ('api_key' not in profile):
            raise AuthError(message='no credentials setup')
        self.api_key = profile['api_key'].strip()
        self.api_key_masked = self.api_key[:4] + '*' * 10 + self.api_key[-4:]
        self.api_server = profile.get('api_server', 'api.rockset.io')
        self.api_server = self.api_server.strip()
        if (
            self.api_server[:7] != 'http://' and
            self.api_server[:8] != 'https://'
        ):
            self.api_server = 'https://{}'.format(self.api_server)
        return (creds, profile)

    def read_stdin(self, what='input'):
        # read from STDIN
        self.lprint(0, 'Enter {} <press ctrl-D to end>:'.format(what))
        lines = []
        while True:
            try:
                line = input("")
            except EOFError:
                break
            lines.append(line)
        return ' '.join(lines)

    def lprint(self, level, *args, **kwargs):
        if level <= self.verbose:
            print(*args, flush=True, **kwargs)

    def eprint(self, level, *args, **kwargs):
        self.lprint(level, *args, file=sys.stderr, **kwargs)

    def error(self, *args, **kwargs):
        self.eprint(0, 'Error %s: ' % self.command, end='')
        self.eprint(0, *args, **kwargs)

    def print_list_yaml(self, level, objs):
        self.lprint(level, yaml.dump(objs))
        return len(objs)

    def print_list_json(self, level, objs):
        for o in objs:
            self.lprint(
                level,
                json.dumps(o, indent=1, separators=(',', ':'), sort_keys=True)
            )
        return len(objs)

    def print_list_text(self, level, objs, field_order, header):
        # use texttable to print tabular view
        table = texttable.Texttable(max_width=120)
        table.set_deco(texttable.Texttable.HEADER)

        # setup headers, list fields in field_order first
        # don't assume field_order fields will always exist
        all_fields = set()
        for o in objs:
            if type(o) is not dict:
                o = o.to_dict()
            all_fields = all_fields.union(o.keys())

        # assemble fields to display using field_order
        # field_order == '*' refers to all fields that are not
        # listed in field_order
        fields = []
        for f in field_order:
            if f == '*':
                fields += all_fields - set(field_order)
            else:
                fields.append(f)
        if len(fields) == 0:
            fields = sorted(list(all_fields))

        # add header if required
        if header == True:
            table.add_row([f.upper().replace('_', ' ') for f in fields])

        # make everything of type text
        table.set_cols_dtype(['t'] * len(fields))

        # setup data rows
        for o in objs:
            c_values = []
            if type(o) is not dict:
                o = o.to_dict()
            for f in fields:
                c_values.append(o.get(f, ''))
            table.add_row(c_values)

        self.lprint(level, table.draw())
        return len(objs)

    def print_list(self, level, objs, field_order=[], header=True, default='text'):
        if objs is None or len(objs) == 0:
            return 0
        if self.format == 'yaml':
            return self.print_list_yaml(level, objs)
        elif self.format == 'json':
            return self.print_list_json(level, objs)
        elif default != 'text':
            if default == 'yaml':
                return self.print_list_yaml(level, objs)
            elif default == 'json':
                return self.print_list_json(level, objs)
        else:
            return self.print_list_text(level, objs, field_order, header)

    def print_one(self, level, one, field_order=[]):
        return self.print_list(level, [one], field_order)
