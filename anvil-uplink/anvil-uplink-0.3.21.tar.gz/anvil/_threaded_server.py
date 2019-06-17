# Helpers for implementing anvil.server on a threaded Real Python process.
# Used in uplink and downlink, but not in pypy-sandbox.

import threading, random, string, json, re, sys, time, importlib, anvil

from . import  _serialise, _server
from ._server import LazyMedia, registrations

string_type = str if sys.version_info >= (3,) else basestring

console_output = sys.stdout

class HttpRequest(threading.local):

    def __init__(self):
        self._prevent_access = True

    def __getattribute__(self, name):
        if threading.local.__getattribute__(self, "_prevent_access"):
            raise Exception("anvil.server.request is only available in http_endpoint calls.")

        return threading.local.__getattribute__(self, name)

_server.api_request = HttpRequest()

def _gen_id():
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))


# Overwrite with functions from context
send_reqresp = None


class LocalCallInfo(threading.local):
    def __init__(self):
        self.call_id = None
        self.stack_id = None
        self.session = None
        self.cache_filter = {}
        self.cache_update = {}

    def __getitem__(self, item):
        return self.session.__getitem__(item)

    def __setitem__(self, key, value):
        return self.session.__setitem__(key, value)

    def __delitem__(self, key):
        del self.session[key]

    def get(self, key, default=None):
        return self.session.get(key, default)

    def __iter__(self):
        return self.session.__iter__()

    def __repr__(self):
        return "<Session:%s>" % repr(self.session)


call_info = LocalCallInfo()
call_responses = {}
waiting_for_calls = threading.Condition()

backends = {}


def _switch_session():
    import anvil.server
    sjson = anvil.server.call('anvil.private.switch_session!') or {"session": {}, "objects": []}
    call_info.session = _server._reconstruct_objects(sjson, None)["session"]


default_app = anvil.app


class LocalAppInfo(threading.local):
    def __init__(self):
        self.__dict__['id'] = default_app.id
        self.__dict__['branch'] = default_app.branch

    def _setup(self, **kwargs):
        self.__dict__.update(kwargs)


anvil.app = LocalAppInfo()


class IncomingRequest(_serialise.IncomingReqResp):
    def __init__(self, json, modules_to_import=None, dump_task_state=False):
        self.modules_to_import = modules_to_import or []
        self.dump_task_state = dump_task_state
        _serialise.IncomingReqResp.__init__(self, json)

    def execute(self):
        def make_call():
            call_info.call_id = self.json.get('id')
            call_info.stack_id = self.json.get('call-stack-id', None)
            sjson = self.json.get('sessionData', {'session': None, 'objects': []})
            call_info.session = None
            call_info.enable_profiling = self.json.get('enable-profiling', False)
            if call_info.enable_profiling:
                call_info.profile = {
                    "origin": "Server (Python)",
                    "description": "Python _threaded_server execution",
                    "start-time": time.time()*1000,
                }
            call_info.cache_filter = _server.get_liveobject_cache_filter_spec([self.json['args'], self.json['kwargs']])
            call_info.cache_update = {}
            anvil.app._setup(**self.json.get('app-info', {}))
            try:
                for n in self.modules_to_import:
                    importlib.import_module(n)

                # Now we've imported enough to deserialise custom types
                self.reconstruct_remaining_data()
                call_info.session = _server._reconstruct_objects(sjson, None).get("session", {})

                if 'liveObjectCall' in self.json:
                    loc = self.json['liveObjectCall']
                    spec = dict(loc)

                    if self.json["id"].startswith("server-"):
                        spec["source"] = "server"
                    elif self.json["id"].startswith("client-"):
                        spec["source"] = "client"
                    else:
                        spec["source"] = "UNKNOWN"

                    del spec["method"]
                    backend = loc['backend']
                    if backend not in backends:
                        raise Exception("No such LiveObject backend: " + repr(backend))
                    inst = backends[backend](spec)
                    method = getattr(inst, loc['method'])

                    call_info.cache_filter.setdefault(backend, set()).add(spec['id'])

                    response = method(*self.json['args'], **self.json['kwargs'])
                else:
                    command = self.json['command']
                    for reg in registrations:
                        m = re.match(reg, command)
                        if m and len(m.group(0)) == len(command):
                            response = registrations[reg](*self.json["args"], **self.json["kwargs"])
                            break
                    else:
                        if self.json.get('stale-uplink?'):
                            raise _server.UplinkDisconnectedError({'type': 'anvil.server.UplinkDisconnectedError',
                                                                   'message':'The uplink server for "%s" has been disconnected' % command})

                        else:
                            raise _server.NoServerFunctionError({'type': 'anvil.server.NoServerFunctionError',
                                                                 'message': 'No server function matching "%s" has been registered' % command})


                def err(*args):
                    raise Exception("Cannot save DataMedia objects in anvil.server.session")

                try:
                    sjson = _server.fill_out_media({'session': call_info.session}, err)
                    json.dumps(sjson)
                except TypeError as e:
                    raise _server.SerializationError("Tried to store illegal value in a anvil.server.session. " + e.args[0])
                except _server.SerializationError as e:
                    raise _server.SerializationError("Tried to store illegal value in a anvil.server.session. " + e.args[0])

                resp = {"id": self.json["id"], "response": response, "sessionData": sjson, "cacheUpdates": call_info.cache_update}

                if call_info.enable_profiling:
                    call_info.profile["end-time"] = time.time()*1000
                    resp["profile"] = call_info.profile

                if self.dump_task_state:
                    try:
                        tjson = _server.fill_out_media({'taskState': anvil.server.task_state}, err)
                        json.dumps(tjson)
                        resp['taskState'] = anvil.server.task_state
                    except (TypeError, _server.SerializationError):
                        pass

                try:
                    send_reqresp(resp)
                except _server.SerializationError as e:
                    raise _server.SerializationError("Cannot serialize return value from function. " + str(e))
            except:

                e = _server._report_exception(self.json["id"])

                if self.dump_task_state:
                    def err(*args):
                        raise Exception("Cannot save DataMedia objects in anvil.server.session")

                    try:
                        tjson = _server.fill_out_media({'taskState': anvil.server.task_state}, err)
                        json.dumps(tjson)
                    except (TypeError, _server.SerializationError):
                        pass
                    else:
                        e['taskState'] = anvil.server.task_state

                try:
                    send_reqresp(e)
                except:
                    trace = "\ncalled from ".join(["%s:%s" % (t[0], t[1]) for t in e["error"]["trace"]])
                    console_output.write(("Failed to report exception: %s: %s\nat %s\n" % (e["error"]["type"], e["error"]["message"], trace)).encode("utf-8"))
                    console_output.flush()
            finally:
                self.complete()

        threading.Thread(target=make_call).start()

    def complete(self):
        pass


class IncomingResponse(_serialise.IncomingReqResp):
    def execute(self):
        id = self.json['id']
        if id in call_responses:
            call_responses[id] = (self, self.json)
            with waiting_for_calls:
                waiting_for_calls.notifyAll()
        else:
            print("Got a response for an unknown ID: " + repr(self.json))


def kill_outstanding_requests(msg):
    for k in call_responses.keys():
        if call_responses[k] is None:
            call_responses[k] = (None, {'error': {'message': msg}})

    with waiting_for_calls:
        waiting_for_calls.notifyAll()


def register_live_object_backend(cls):

    name = "uplink." + cls.__name__
    backends[name] = cls

    if _server.on_register is not None:
        _server.on_register(name, True)

    return cls


live_object_backend = register_live_object_backend


def do_call(args, kwargs, fn_name=None, live_object=None): # Yes, I do mean args and kwargs without *s
    id = _gen_id()

    call_responses[id] = None

    profile = {
        "origin": "Server (Python)",
        "description": "Outgoing call from Python _threaded_server",
        "start-time": time.time()*1000
    }
    with waiting_for_calls:
        # print("Call stack ID = " + repr(_call_info.stack_id))
        if call_info.stack_id is None:
            call_info.stack_id = "outbound-" + _gen_id()
        req = {'type': 'CALL', 'id': id, 'args': args, 'kwargs': kwargs,
               'call-stack-id': call_info.stack_id, 'originating-call': call_info.call_id}

        if live_object:
            req["liveObjectCall"] = { k: live_object._spec[k] for k in ["id", "backend", "mac", "permissions"] }
            req["liveObjectCall"]["method"] = fn_name
        elif fn_name:
            req["command"] = fn_name
        else:
            raise Exception("Expected one of fn_name or live_object")
        try:
            send_reqresp(req)
        except _server.SerializationError as e:
            raise _server.SerializationError("Cannot serialize arguments to function. " + str(e))

        while call_responses[id] is None:
            waiting_for_calls.wait()

    profile["end-time"] = time.time()*1000

    reqresp, r = call_responses.pop(id)

    # Now we're in the right thread, we can do any custom deserialisation
    if reqresp:
        reqresp.reconstruct_remaining_data()

    if "cacheUpdates" in r:
        # Apply updates to any of our own objects that were passed in
        _server.apply_cache_updates(r['cacheUpdates'], [args, kwargs, live_object])
        # Queue up whichever updates *we* should be returning
        _server.combine_cache_updates(call_info.cache_update, r['cacheUpdates'], call_info.cache_filter)

    if "profile" in r:
        profile["children"] = [r["profile"]]

    if hasattr(call_info, "profile"):
        if "children" not in call_info.profile:
            call_info.profile["children"] = []

        call_info.profile["children"].append(profile)

    if 'response' in r:
        return r['response']
    if 'error' in r:
        raise _server._deserialise_exception(r["error"])
    else:
        raise Exception("Bogus response from server: " + repr(r))
