# -*- coding: utf-8 -*-
from lektor.pluginsystem import Plugin


def nf_resize(source, nf_resize='fit', h='', w=''):
	if nf_resize == 'fit' or nf_resize == 'smartcrop':
		if h and not w:
			return source + '?nf_resize=' + nf_resize + '&h=' + str(h)
		elif not h and w:
			return source + '?nf_resize=' + nf_resize + '&w=' + str(w)
		elif h and w:
			return source + '?nf_resize=' + nf_resize + '&h=' + str(h) + '&w=' + str(w)
		else:
			return source
	else:
		return source

class NetlifyLfsResizeUrlPlugin(Plugin):
	name = 'netlify-lfs-resize-url'
	description = u'Convert image URLs to Netlify LFS resize URLs.'

	def on_process_template_context(self, context, **extra):
		def test_function():
			return 'Value from plugin %s' % self.name
		context['test_function'] = test_function

	def on_setup_env(self, **extra):
		self.env.jinja_env.filters['nf_resize'] = nf_resize
		#self.env.jinja_env.globals.update(nf_resize=nf_resize)
