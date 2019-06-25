#!/usr/bin/python3

import argparse
import logging
import json
import os.path
import datetime

from twisted.web.resource import Resource, NoResource
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.util import redirectTo
from twisted.internet import reactor
from twisted.internet.error import CannotListenError

from volcano.general.log import configure_arg_parser_for_log, configure_logger
from volcano.general import stdsvcdef
from volcano.general.xml_reader import LoadException
from volcano.general.stddef import VOLCANO_DEFAULT_TCP_PORT, ValueType
from volcano.general import variant
from volcano.general.stdsvc import SingleThreadAllService

from volcano.twistedclient.twisted_factory import VolcanoTwistedFactory
from volcano.twistedclient.twisted_client_st import VolcanoTwistedClientST


def configure_my_args(parser):
    parser.add_argument('--core_host', help='Volcano core host', default='localhost')
    parser.add_argument('--core_port', help='Volcano core port', default=VOLCANO_DEFAULT_TCP_PORT, type=int)
    parser.add_argument('-n', '--name', help='Instance name', default='web')
    parser.add_argument('-i', '--iface', help='Listen interface', default='')  # twisted.listenTcp (..iface='') defaults to all
    parser.add_argument('-p', '--port', help='Listen port', default=8080, type=int)
    parser.add_argument('-w', '--www', help='Static files', default=None)
    parser.add_argument('-c', '--ctrl', help='Enable remote control', action='store_true')
    #parser.add_argument('-g', '--get', help='Enable remote control over GET verb', action='store_true')


class Tag:
    def __init__(self, parent_none, short_name, var, atts):
        assert isinstance(var, variant.Variant), var

        self.parent_ = parent_none  # can be None
        self.short_name_ = short_name  # always non-empty
        self.var = var
        self.atts = atts
        self.quality = None
        self.tstamp = None
        self.children = []

    def parent(self):
        return self.parent_

    def short_name(self):
        return self.short_name_

    def full_name(self):
        return self.short_name_ if self.parent_ is None else (self.parent_.full_name() + '.' + self.short_name_)


class Db:
    def __init__(self):
        self.all_tags_by_name = {}
        self.root_tags_list = []

    def find(self, full_name):
        return self.all_tags_by_name.get(full_name, None)

    def add(self, tag_name, var, atts):
        tag = None

        names = tag_name.split('.')
        if len(names) == 1:
            tag = Tag(None, tag_name, var, atts)
            self.root_tags_list.append(tag)
        else:
            parent_name = '.'.join(names[0:-1])
            short_name = names[-1]
            parent = self.find(parent_name)
            assert parent
            tag = Tag(parent, short_name, var, atts)
            parent.children.append(tag)

        self.all_tags_by_name[tag.full_name()] = tag

        return tag


class WebException(Exception):
    def __init__(self, message, http_code=400):
        super().__init__(message)
        self.http_code = http_code


class Args:     # pylint: disable=too-few-public-methods
    def __init__(self, req):
        self.req_ = req

    def get_str(self, name, default=None):
        val = self.req_.args.get(name.encode('utf-8'), None)
        if val is None or not val:  # val is none or list[]
            if default is None:
                raise WebException('Missing "{}" argument'.format(name), 400)
            return default

        assert isinstance(val, list)
        return val[0].decode('utf-8')


class VolcanoJsonService(Resource):
    isLeaf = True

    def get_json(self, request):
        pass

    def render_GET(self, request):
        try:
            res = self.get_json(request)    # pylint: disable=assignment-from-no-return
        except WebException as ex:  # other exceptions produce html page with call stack
            request.setHeader(b'content-type', b'text/plain')
            request.setResponseCode(ex.http_code)
            return str(ex).encode('utf-8')

        request.setHeader(b'content-type', b'application/json')
        return json.dumps(res).encode('utf-8')


class CmdInfo(VolcanoJsonService):
    def get_json(self, request):
        return {
            "version": {
                "major": 1,
                "minor": 1,
                "patch": 1,
            },
            "web": {
                "ctrl": g_env.ctrl,
                "remoteStop": False,
            }
        }


class CmdLs(VolcanoJsonService):
    def get_json(self, request):
        args = Args(request)
        tag_name = args.get_str('tag', '')  # throws WebException
        tags_list = None
        if not tag_name:  # list root
            tags_list = g_db.root_tags_list
        else:
            tag = g_db.find(tag_name)
            if not tag:
                raise WebException('Tag "{}" not found'.format(tag_name), 400)
            tags_list = tag.children
        return list(map(lambda x: x.short_name(), tags_list))


class CmdStat(VolcanoJsonService):
    def get_json(self, request):
        args = Args(request)

        tag_name = args.get_str('tag')  # throws WebException
        data = args.get_str('d', '')

        tag = g_db.find(tag_name)
        if not tag:
            raise WebException('Tag "{}" not found'.format(tag_name), 400)

        res = {}

        # title, eu, id, children, parents
        if 't' in data:
            res['type'] = tag.var.type_str()
        if 'T' in data:
            res['title'] = tag.atts.get('title', '')
        if 'n' in data:
            res['name'] = tag.short_name()
        if 'N' in data:
            res['fullName'] = tag.full_name()
        if 'c' in data:
            res['hasChildren'] = len(tag.children) > 0  # pylint: disable=len-as-condition

        return res


class CmdRead(VolcanoJsonService):
    def get_json(self, request):
        args = Args(request)

        tag_name = args.get_str('tag')  # throws WebException
        tag = g_db.find(tag_name)

        if not tag:
            raise WebException('Tag "{}" not found'.format(tag_name), 400)

        if tag.var.is_void():
            raise WebException('Tag "{}" is VOID'.format(tag_name), 400)

        return {
            'v': tag.var.get_value(),
            'q': tag.quality,
            #'t': '{}Z'.format(tag.tstamp.isoformat(timespec='milliseconds')) if tag.tstamp else None,
            # isoformat with timespec is Python 3.6
            't': (tag.tstamp.isoformat() + 'Z') if tag.tstamp else None,
        }
        
        
class CmdWrite(VolcanoJsonService):
    isLeaf = True
    
    def render_GET(self, request):
        '''
            На данный момент управление возможно через GET по следующим причинам:
                - удобно тестировать через браузер
                - сама по себе фича все равно отладочная
        '''
        #request.setHeader(b'content-type', b'text/plain')
        #request.setResponseCode(400)
        #return 'Use POST to set '.encode('utf-8')
        return self.render_POST(request)

    def render_POST(self, request):  # pylint: disable=no-self-use
        try:
            args = Args(request)    # !WebException
            
            tag_name = args.get_str('tag')  # !WebException
            tag_val = args.get_str('val')  # !WebException
            tag = g_db.find(tag_name)

            if not tag:
                raise WebException('Tag "{}" not found'.format(tag_name), 404)

                
            # env.ctrl is not checked because otherwise CmdWrite handler wont be added

            # Convert value
            proper_value = None
            if tag.var.vt() == ValueType.VT_BOOL:
                if tag_val == '1':
                    proper_value = True
                elif tag_val == '0':
                    proper_value = False
                else:
                    raise WebException('Cant convert value "{}" to type {} of tag "{}". Use "1" and "0"'.format(tag_val, tag.var.vt(), tag_name), 400)
            elif tag.var.vt() == ValueType.VT_INT:
                try:
                    proper_value = int(tag_val)
                except ValueError as ex:
                    raise WebException('Cant convert value "{}" to type {} of tag "{}"'.format(tag_val, tag.var.vt(), tag_name), 400)
            elif tag.var.vt() == ValueType.VT_FLOAT:
                try:
                    proper_value = float(tag_val)
                except ValueError as ex:
                    raise WebException('Cant convert value "{}" to type {} of tag "{}"'.format(tag_val, tag.var.vt(), tag_name), 400)
            elif tag.var.vt() == ValueType.VT_STR:
                proper_value = tag_val
            else:
                raise WebException('Tag "{}" is VOID'.format(tag_name), 400)
            
            MyLavaClient.Inst.set_tag(tag_name, proper_value)
            
            request.setHeader(b'content-type', b'text/plain')
            return 'OK'.encode('utf-8')
            
        except WebException as ex:  # other exceptions produce html page with call stack
            request.setHeader(b'content-type', b'text/plain')
            request.setResponseCode(ex.http_code)
            return str(ex).encode('utf-8')


class MyLavaClient(VolcanoTwistedClientST, stdsvcdef.ITagIterHandler, stdsvcdef.ITagUpdateHandler):
    Inst = None

    def __init__(self):
        super().__init__(logging.getLogger(g_env.name))
        self.all_svc_ = None

    def on_msg_rcvd_no_exc(self, msg: dict) -> None:   # Exceptions not expected
        self.all_svc_.push_single_message(msg)

    def connectionMade(self):
        
        MyLavaClient.Inst = self
        
        super().connectionMade()

        self.all_svc_ = SingleThreadAllService(self)
        self.all_svc_.salute(g_env.name)

        self.all_svc_.first(self)

    def on_next_tag(self, tag_id: int, tag_name: str, vt: str, atts: dict):
        g_db.add(tag_name, variant.Variant.from_vt(ValueType(vt)), atts)

        self.all_svc_.next(tag_id, self)

    def on_next_end(self):
        self.log.info('Sync finished')
        self.all_svc_.subscribe_all(send_tstamp=True, use_tag_id=False, handler=self)

        if g_env.www:
            self.log.info('Start listen: iface={} port={} static={}'.format(g_env.iface, g_env.port, g_env.www))
        else:
            self.log.info('Start listen: iface={} port={}'.format(g_env.iface, g_env.port))

        try:
            reactor.listenTCP(g_env.port, g_http_factory, interface=g_env.iface)    # pylint: disable=no-member
        except CannotListenError as ex:
            self.log.error(ex)
            reactor.stop()  # pylint: disable=no-member

    def on_next_err(self):
        raise Warning('Failed enumerating')

    def on_tag_updated(self, tag_name_or_id: (int, str), val_raw, quality: int, tstamp_n: (datetime.datetime, None)):
        tag = g_db.find(tag_name_or_id)
        if tag:
            tag.var.set_value_w(val_raw)
            tag.quality = quality
            tag.tstamp = tstamp_n

    def set_tag(self, tag_name_or_id, tag_val):
        self.all_svc_.set_tag(tag_name_or_id, tag_val)


class MyLavaFactory(VolcanoTwistedFactory):
    protocol = MyLavaClient


class IndexResource(Resource):
    def render_GET(self, request):  # pylint: disable=no-self-use
        return redirectTo(b'/www/index.html', request)


class FaviconResource(Resource):
    def render_GET(self, request):  # pylint: disable=no-self-use
        return redirectTo(b'/www/favicon.ico', request)


class MyWebRoot(Resource):
    index = IndexResource()
    favicon = FaviconResource()

    def getChild(self, path, request):
        if g_env.www and path in (b'', b'index.html'):
            return self.index

        if g_env.www and (path == b'favicon.ico'):
            return self.favicon

        resp = Resource.getChild(self, path, request)
        if isinstance(resp, NoResource):
            g_log.warning('Not found %s', path)
        return resp


if __name__ == '__main__':
    # Args
    arg_parser = argparse.ArgumentParser()
    configure_my_args(arg_parser)
    configure_arg_parser_for_log(arg_parser)  # let logger add his arguments for later configure_logger() call
    g_env = arg_parser.parse_args()

    # Logging
    configure_logger(g_env)
    g_log = logging.getLogger(g_env.name)

    if g_env.www:
        if not os.path.isdir(g_env.www):
            g_log.error('Static files directory (-w -www) not found: %s', g_env.www)
    else:
        my_path = os.path.dirname(__file__)
        assert my_path
        g_env.www = my_path + '/www'

        if os.path.isdir(g_env.www):
            g_log.info('Default www path is used: %s', g_env.www)
        else:
            g_log.error('Default www path not found: %s', g_env.www)

    g_log.info('Remote control is %s', 'ON' if g_env.ctrl else 'OFF')
    

    try:
        g_db = Db()
        g_http_factory = None
        volcano_factory = MyLavaFactory()
        volcano_factory.log = g_log

        root = MyWebRoot()

        if g_env.www:
            root.putChild(b'www', File(g_env.www))

        root.putChild(b'info.json', CmdInfo())
        root.putChild(b'ls.json', CmdLs())
        root.putChild(b'stat.json', CmdStat())
        root.putChild(b'read.json', CmdRead())
        
        if g_env.ctrl:
            root.putChild(b'set', CmdWrite())

        g_http_factory = Site(root)

        g_log.info('Connect to core at %s:%s', g_env.core_host, g_env.core_port)
        reactor.connectTCP(g_env.core_host, g_env.core_port, volcano_factory)   # pylint: disable=no-member
        reactor.run()       # pylint: disable=no-member

    except (LoadException, Warning) as ex:
        g_log.error(ex)

    finally:
        logging.shutdown()
