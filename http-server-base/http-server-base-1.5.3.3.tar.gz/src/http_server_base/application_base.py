import multiprocessing
import re
from typing import Tuple, List, Type, Set, Callable, Union, Any, Dict
from logging import getLogger, Logger
import socket
from camel_case_switcher import dict_keys_camel_case_to_underscore
import copy

from http_server_base import BasicResponder, HandlerController, HandlerListType, Logged_RequestHandler, IResponder
from http_server_base.empty_request_handler import Empty_RequestHandler
from http_server_base.health_check_request_handler import HealthCheck_RequestHandler
from http_server_base.tools import ExtendedLogger, RequestLogger
from http_server_base.tools.config_loader import ConfigLoader

from tornado.httpserver import HTTPServer, HTTPRequest
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from ssl import SSLContext, Purpose, create_default_context

class _Protocols:
    __http = 'http'
    __https = 'https'
    
    http = __http
    HTTP = __http
    
    https = __https
    HTTPS = __https

class ApplicationBase(Application):
    """
    ApplicationBase class.
    
    The following attributes can be overrided:
    :attribute logger_name
    :attribute handlers
    List of handlers those are passed to the to tornado.web.Application class during the initialisation.
    If untouched (None or missing), default handlers will be used.
    """
    name: str
    logger_name:str = 'http_server'
    access_logger_name: str = None
    handlers: HandlerListType
    handler_controllers: List[HandlerController]
    hosts:List[str]
    bind_address: str = None
    responder_class: Type[IResponder] = BasicResponder
    new_format_access_log: bool = False
    
    ssl_enabled: bool = None
    ssl_options: Union[SSLContext, Dict[str, Any], None] = None
    ssl_certificate_path: str = None
    ssl_private_key_path: str = None
    
    default_handlers = \
    [
        (r"^/?$", Empty_RequestHandler, dict(redirect_page='/static/index.html')),
        (r"^/healthcheck(|(/.*))$", HealthCheck_RequestHandler),
    ]
    
    __logger: ExtendedLogger = None
    __access_logger: ExtendedLogger = None
    __server: HTTPServer = None
    
    __self_addr: str = None
    __listen_port: int = None
    __protocol:str = None
    
    #region Initialization
    def __init__(self, *,
            name:str = None,
            config_name:str='main', config_prefix='HTTP', config_priority=False,
            hosts:List[str]=None, bind_address:str=None,
            handler_controllers:List[HandlerController]=None,
            handlers:HandlerListType=None,
            **settings):
        """
        Initializes a new instance of tornado.web.Application and prepares tornado.httpserver.HTTPServer to be run.
        :param name:
        str. Name of server used in serveral log records.
        
        :param config_name:
        Name of config in the ConfigLoader class, where the settings are loaded from.
        By default, settings are loaded from the main config.
        :param config_prefix:
        Prefix part of the config path to the server's settings. Path keys are '/'-separated.
        Note that due to the implementation's restrictions, server settings could not be in the top-level of the config.
        :param config_priority:
        By default, arguments passed directly to the initializer, have more priority.
        By setting config_config_priority=True, you are prioritising config over the keyword arguments.
        
        :param hosts
        List of str.
        :param bind_address
        str or None. The address the core server is bound.
        :param handler_controllers
        List of HandlerController initialized objects
        
        :param settings:
        Keyword arguments. Partially parsed by ApplicationBase, partially passed to the tornado.web.Application
        All ApplicationBase optional parameters are listed below.
        Note that all CamelCase parameters loaded from the config would be morphed into the underscore_style,
            so `selfAddress` and `ListenPort` are completely legal.
        
        :param static_files:
        Same as `static_path`.
        If both are presented, `static_path` has priority.
        
        :param self_address:
        str. Hardcoded server uri. Used only for the info message about server start and several responses based on the `self_address` property.
        Should contain protocol.
        :param listen_ip:
        str. Used only if `self_address` is not set up for the `self_address` calculation.
        If missing as well, server will try to self-discover.
        The resulting self_address will have protocol - http or https, ip-address and, if custom, a port.
        :param ip:
        Same as `listen_ip`.
        If both are presented, `listen_ip` has priority.
        :param listen_port:
        int value of port, which server is uses to listen requests.
        By default 80 or 443 port is used - according to the SSL configuration
        :param port:
        Same as `listen_port`.
        If both are presented, `listen_port` has priority.
        
        :param ssl: Union[Dict[str, Any], SSLContext, None]
        If dict, has same effect as ssl_ parameters below:
        :param ssl_options:
        Same as `ssl`
        :param ssl_enabled: bool
        Enables SSL.
        Default: True if ssl/ssl_options are defined, False otherwise
        :param ssl_certificate_path: str
        Loaded only is ssl is enabled
        Path to public certificate/key path
        Default: 'configs/public-cert.crt' if ssl is enabled
        :param ssl_private_key_path: str
        Loaded only is ssl is enabled
        Path to private certificate/key path
        Default: 'configs/private-key.key' if ssl is enabled
        """
        
        # TODO: Hosts description
        # TODO: Handlers description
        # TODO: Handler Controllers description
        
        if (name is not None):
            self.name = name
        if (not hasattr(self, 'name') or self.name is None):
            self.name = type(self).__name__
        if (handler_controllers is not None):
            self.handler_controllers = handler_controllers
        if (not hasattr(self, 'handler_controllers') or self.handler_controllers is None):
            self.handler_controllers = list()
        
        if (bind_address is not None):
            self.bind_address = bind_address
        if (not hosts is None):
            self.hosts = hosts
        if (not hasattr(self, 'hosts') or self.hosts is None):
            self.hosts = [ 'self' ]

        self.__logger: ExtendedLogger = getLogger(self.logger_name)
        if (not hasattr(self, 'access_logger_name') or self.access_logger_name is None):
            self.access_logger_name = f'{self.logger_name}.access'
        _access_logger: ExtendedLogger = getLogger(self.access_logger_name)
        self.__access_logger: RequestLogger = RequestLogger(None, _access_logger)
        
        if (handlers is not None):
            self.handlers = handlers
            self.logger.debug(f"{self.name}: List of handlers: {handlers}")
        elif (getattr(self, 'handlers', None) is not None):
            self.logger.debug(f"{self.name}: List of handlers: {self.handlers}")
        else:
            self.handlers = ApplicationBase.default_handlers
            self.logger.debug(f"{self.name}: Using default handlers")
        
        _settings = dict_keys_camel_case_to_underscore(ConfigLoader.get_from_config(config_prefix, config_name=config_name, default=lambda: dict()), recursive=True)
        if (config_priority):
            settings_deep_copy = copy.deepcopy(settings)
            settings_deep_copy.update(_settings)
            _settings = settings_deep_copy
        else:
            _settings.update(settings)
        
        if (_settings.get('static_files') and not _settings.get('static_path')):
            _settings['static_path'] = _settings['static_files']
        
        self.initialize_ssl(_settings)
        extra = self.initialize_host(_settings)
        super().__init__(handlers=self.handlers, **_settings)
        self.attach_controllers(_settings, **extra)
    
    def initialize_ssl(self, settings):
        if (self.ssl_options is None):
            self.ssl_options = settings.get('ssl_options') or settings.get('ssl')
        if (isinstance(self.ssl_options, dict)):
            self.ssl_enabled = self.ssl_options.pop('enabled', None)
            self.ssl_certificate_path = self.ssl_options.pop('certificate_path', None)
            self.ssl_private_key_path = self.ssl_options.pop('private_key_path', None)
            if (not self.ssl_options):
                self.ssl_options = None
        
        if (self.ssl_options is None):
            if (self.ssl_enabled is None):
                self.ssl_enabled = settings.get('ssl_enabled', False)
            if (self.ssl_enabled):
                if (self.ssl_certificate_path is None):
                    self.ssl_certificate_path = settings.get('ssl_certificate_path', 'configs/public-cert.crt')
                if (self.ssl_private_key_path is None):
                    self.ssl_private_key_path = settings.get('ssl_private_key_path', 'configs/private-key.key')
                self.ssl_options = create_default_context(Purpose.CLIENT_AUTH)
                self.ssl_options.load_cert_chain(self.ssl_certificate_path, self.ssl_private_key_path)
        elif (isinstance(self.ssl_options, (dict, SSLContext))):
            self.ssl_enabled = True
        else:
            raise ValueError(f"SSL config must be either dict, SSLContext, or None, not '{type(self.ssl_options)}'")
    
    def initialize_host(self, settings):
        if (self.ssl_enabled):
            protocol = _Protocols.HTTPS
        else:
            protocol = _Protocols.HTTP
        
        listen_port = settings.get('listen_port') or settings.get('port')
        if (listen_port is None):
            if (protocol == _Protocols.HTTP):
                listen_port = 80
            elif (protocol == _Protocols.HTTPS):
                listen_port = 443
            listen_port_part = ""
        else:
            listen_port_part = f":{listen_port}"
    
        self.__listen_port = listen_port
        
        return dict(protocol=protocol, listen_port_part=listen_port_part)
    
    def attach_controllers(self, settings:dict, *, protocol, listen_port_part, **kwargs):
        for host in self.hosts:
            host_address = settings.get(f'{host}_address')
            host_pattern = None
            
            if (host_address):
                listen_address = None
            else:
                if (hasattr(self, f'get_{host}_host') and callable(getattr(self, f'get_{host}_host'))):
                    _host = getattr(self, f'get_{host}_host')()
                    if (isinstance(_host, tuple) and len(_host) == 2):
                        listen_address, host_pattern = _host
                    else:
                        # TODO: ?!?!?!
                        listen_address = result
                else:
                    listen_address = \
                        settings.get('listen_address') \
                        or settings.get('listen_ip') \
                        or settings.get('ip') \
                        or socket.gethostbyname(socket.gethostname()) \
                    ;
                host_address = f"{protocol}://{listen_address}{listen_port_part}"
        
            setattr(self, f'_{type(self).__name__}__{host}_addr', host_address)
            if (not hasattr(self, f'{host}_address')):
                setattr(type(self), f'{host}_address', host_address)
            
            if (host_pattern is None):
                if (listen_address is None):
                    host_pattern = '.*'
                else:
                    host_pattern = re.escape(listen_address)

            host_handlers = list()
            for _handler_controller in self.handler_controllers:
                getter = getattr(_handler_controller, f'get_{host}_handlers')
                _handlers = getter()
                host_handlers += _handlers

            self.add_handlers(re.compile(host_pattern, re.IGNORECASE), host_handlers)
    def initialize_settings(self):
        pass
    #endregion
    
    @property
    def logger(self) -> ExtendedLogger:
        return self.__logger
    
    #region Discovery
    @classmethod
    def __self_discover_generator(cls):
        names = \
        [
            'localhost',
            socket.getfqdn(),
        ]
        for name in names:
            try:
                for _value in cls.__self_discover_generator_per_interface(name=name):
                    yield _value
            except socket.herror:
                continue
        
        local_addr = cls.get_public_ip()
        try:
            for _value in cls.__self_discover_generator_per_interface(addr=local_addr):
                yield _value
        except socket.herror:
            pass
    
    @classmethod
    def __self_discover_generator_per_interface(cls, name=None, addr=None):
        if (addr is None):
            assert not name is None, "Either name or addr is required"
            addr = socket.gethostbyname(name)
        yield addr
        _name, _alias_list, _address_list = socket.gethostbyaddr(addr)
        yield _name
        for _alias in _alias_list:
            yield _alias
        for addr in _address_list:
            yield addr
            yield socket.getfqdn(_name)
            yield socket.gethostbyname(_name)
    
    @classmethod
    def get_public_ip(cls):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_addr = s.getsockname()[0]
            s.close()
            return local_addr
        except OSError:
            return socket.gethostbyname(socket.gethostname())
            
    @classmethod
    def self_discover(cls) -> Set[str]:
        """
        Server will try to do some self-discovery job.
        Not used in the distributed version.
        
        :return:
        The result is non-sorted set of unique items which could be associated with the local host.
        Usually it looks like:
        { '127.0.0.1', '127.0.1.1', 'localhost', 'MyComputer', '192.168.0.14' }
        """
        
        return set(cls.__self_discover_generator())

    @property
    def listen_port(self) -> int:
        return self.__listen_port
    
    def get_self_host(self) -> Tuple[str, str]:
        return self.get_public_ip(), '.*'
    
    @property
    def self_address(self) -> str:
        """
        Returns the self_address value, which was calculated during the initialisation process.
        :return:
        Returns self_address value.
        """
        
        return getattr(self, f"_{type(self).__name__}__self_addr")
    #endregion
    
    #region Start server
    def run(self, blocking=True, num_processes=1):
        """
        Runs the server on the port specified earlier.
        Server blocks the IO.
        """
        
        self.logger.info(f"{self.name}: Starting HTTP service...")
        
        self.__server = HTTPServer(self, ssl_options=self.ssl_options)
        self.__server.listen(self.__listen_port, address=self.bind_address)
        self.logger.info(f"{self.name}: Service started")
        for host in self.hosts:
            host_address = getattr(self, f'{host}_address')
            self.logger.info(f"{self.name}: Listening on the {host} host: {host_address}")
        
        self.__server.start(num_processes=num_processes)
        
        if (blocking):
            IOLoop.current().start()
    
    @classmethod
    def simple_start_decorator_with_settings(cls, **settings):
        """
        Decorator creator with settings.
        
        Resulting decorator turns function into the simple server start method.
        It initializes logging and ConfigLoader in the soft-mode,
        than initializes the class instance, runs this function and starts the server.

        :param settings:
        Settings used for the server initialization
        :return:
        The decorator to the function to start the server
        
        Example usage:
        @ApplicationBase.simple_start_decorator_with_settings(port=8123, static_files='static', debug=True)
        def my_func(server_app):
            server_app.logger.debug(f"{self.name}: I am going to be run")
        
        """
        return lambda func: cls.simple_start_decorator(func, **settings)
        
    @classmethod
    def simple_start_decorator(cls, pre_run_func:Callable[['ApplicationBase', Any], None], **settings) -> Callable[[Any], None]:
        """
        Decorator that turn function into the simple server start method.
        It initializes logging and ConfigLoader in the soft-mode,
        than initializes the class instance, runs this function and starts the server.
        
        :param pre_run_func:
        Function to be run after the server initialization but before actual start.
        Any arguments are allowed.
        :param settings:
        Settings used for the server initialization
        :return:
        The function to start the server
        """
        
        def wrapper(*args, **kwargs):
            cls.simple_start_server(lambda server_application: pre_run_func(server_application, *args, **kwargs), **settings)
        return wrapper
    
    @classmethod
    def simple_start_prepare(cls):
        from logging import getLogger
        from http_server_base.tools import setup_logging
    
        # Configure logger
        setup_logging()
        logger = getLogger(cls.logger_name)
        logger.setLevel('TRACE')
        logger.info("Logger started")
        ConfigLoader.load_configs(soft_mode=True)
        
        return logger

    @classmethod
    def __simple_start_func(cls, pre_run_func:Union[Callable[['ApplicationBase'], None], None], num_processes=1, blocking=True, **settings) -> Tuple[Union['ApplicationBase', None], Union[Exception, None]]:
        """
        If any expected error occurs, returns the instance of initialized class (if any) and the exception
        
        :param pre_run_func:
        Function to be run after the server initialization but before actual start.
        Must take only one argument - the server instance.
        :param settings:
        Settings used for the server initialization
        :return:
        Tuple:
         - instance of initialized object (if any)
         - exception info
        """
        
        server_application:ApplicationBase = cls(**settings)
        if (callable(pre_run_func)):
            pre_run_func(server_application)
    
        try:
            server_application.run(num_processes=num_processes, blocking=blocking)
        except KeyboardInterrupt:
            server_application.logger.info("Keyboard interrupt. Exiting now.")
        except PermissionError as e:
            return server_application, e
        
        return None, None

    @classmethod
    def simple_start_server(cls, pre_run_func:Union[Callable[['ApplicationBase'], None], None] = None, **settings):
        """
        Initializes logging and ConfigLoader in the soft-mode,
        than initializes the class instance, runs this function and starts the server.

        :param pre_run_func:
        Function to be run after the server initialization but before actual start.
        Must take only one argument - the server instance.
        :param settings:
        Settings used for the server initialization
        :return:
        """
        
        logger = cls.simple_start_prepare()
        
        try:
            server_application, exception = cls.__simple_start_func(pre_run_func, **settings)
            
            if (isinstance(exception, PermissionError)):
                server_application.logger.error("Permission error. Restarting server with the port of range 8xxx.")
                new_port = server_application.listen_port + 8000
                del server_application
                settings['listen_port'] = new_port
                logger.info(f"Restarting server on the port {new_port}.")
                cls.__simple_start_func(pre_run_func, **settings)
                
                
        except Exception:
            logger.exception(msg="Unhandled exception while starting server:")
            raise
    #endregion
    
    def find_handler(self, request: HTTPRequest, **kwargs):
        self.normalize_request(request)
        return super().find_handler(request, **kwargs)
    
    def normalize_request(self, request: HTTPRequest):
        path, sep, query = request.uri.partition('?') # type: str, str, str
        _new_path = '/'.join([''] + [_part for _part in path.split('/') if _part])
        if (path.endswith('/')):
            _new_path += '/'
        if (_new_path != path):
            _new_uri = _new_path + sep + query
            self.logger.trace(f"Rewriting uri: '{path}' => '{_new_path}'")
            request.uri = _new_uri
            request.path = _new_path
    
    #region Logging
    def log_request(self, *args, **kwargs):
        method = self._log_request_new if (self.new_format_access_log) else super().log_request
        return method(*args, **kwargs) 
    
    def _log_request_new(self, handler: Logged_RequestHandler):
        if ('log_function' in self.settings):
            self.settings['log_function'](handler)
            return
        
        _logger = self.__access_logger
        if (handler.get_status() < 400):
            log_method = _logger.info
        elif (handler.get_status() < 500):
            log_method = _logger.warning
        else:
            log_method = _logger.error
        request_time = 1000.0 * handler.request.request_time()
        log_method("%d %s %.2fms", handler.get_status(), handler._request_summary(), request_time, style='%', prefix='resp', request_id=handler.request_id)
    #endregion
