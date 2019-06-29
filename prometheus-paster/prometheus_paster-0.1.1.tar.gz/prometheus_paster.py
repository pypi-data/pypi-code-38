import re
import itertools
import functools
from paste.deploy.converters import asbool
from prometheus_client import make_wsgi_app, Summary, Histogram
from prometheus_client.context_managers import Timer

def factory(global_config, **local_conf):
	return make_wsgi_app()

def filter_factory(global_config, **local_conf):
	latency_name = local_conf.get("latency")
	if not latency_name:
		latency_name = "response_latency_seconds"
	latency_metric = None
	if not asbool(local_conf.get("disable_latency")):
		latency_metric = Histogram(latency_name, "Response latency (seconds)", ["method", "status"])
	
	length_name = local_conf.get("length")
	if not length_name:
		length_name = "response_length_bytes"
	length_metric = None
	if not asbool(local_conf.get("disable_length")):
		length_metric = Summary(length_name, "Response length (bytes)", ["method", "status"])
	
	path_regex = local_conf.get("path_regex", ".*")
	
	def middleware(application):
		@functools.wraps(application)
		def wsgiapp(environ, start_response):
			if not re.match(path_regex, environ.get("SCRIPT_NAME","")+environ.get("PATH_INFO","")):
				return application(environ, start_response)
			
			extra = {
				"method": environ["REQUEST_METHOD"],
			}
			
			class Sentinel(object):
				def __init__(self):
					self.length = 0
				
				def __iter__(self):
					if length_metric:
						length_metric.labels(**extra).observe(self.length)
					raise StopIteration()
			
			sentinel = Sentinel()
			
			@functools.wraps(start_response)
			def sr_proxy(status, resp_headers, exc_info=None):
				try:
					extra["status"], _ = status.split(None, 1)
				except ValueError:
					extra["status"] = status
				
				write = start_response(status, resp_headers, exc_info)
				if length_metric:
					@functools.wraps(write)
					def write_proxy(body_data):
						sentinel.length += len(body_data)
						return write(body_data)
					
					return write_proxy
				else:
					return write
			
			def cb(duration):
				if latency_metric:
					latency_metric.labels(**extra).observe(duration)
			
			with Timer(cb):
				obj = application(environ, sr_proxy)
				if length_metric:
					def count_length(body_data):
						sentinel.length += len(body_data)
						return body_data
					
					return itertools.chain(map(count_length, obj), sentinel)
				else:
					return obj
		
		return wsgiapp
	
	return middleware

