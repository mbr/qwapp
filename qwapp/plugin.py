#!/usr/bin/env python
# coding=utf8

from functools import wraps
import re

BLOCK_EXPRESSION = r'\[{\s*(%s)\b(.*)}\]'

def make_block_expression(name):
	return re.compile(BLOCK_EXPRESSION % name, re.S)

class Plugin(object):
	def __init__(self, name = 'Unnamed plugin', author = 'Unnamed author', description = 'No description', version = (0, 1)):
		self.signal_map = {}
		self.name = name
		self.author = author
		self.description = description
		self.version = version

	def on_signal(self, signal_name):
		def wrap_func(f):
			self.signal_map.setdefault(signal_name, []).append(f)
			return f

		return wrap_func

	def register_app(self, app):
		for signal_name, receivers in self.signal_map.iteritems():
			sig = app.plugin_signals[signal_name]
			for f in receivers:
				sig.connect(f)

		app.plugin_signals['plugin-loaded'].send(self, app = app)
		app.plugins.append(self)

	@property
	def version_string(self):
		return u'%s %s' % (self.name, '.'.join(str(v) for v in self.version))
