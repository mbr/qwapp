#!/usr/bin/env python
# coding=utf8

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

from flask import current_app

from qwapp.plugin import Plugin

plugin = Plugin('Headershift', author = 'Marc Brinkmann', description = 'Shifts headers down a level, so they do not interfere with the page header.', version = (0,1))

@plugin.on_signal('page-treeprocess')
def process(page):
	for elem in page.body.getiterator():
		if elem.tag in ('h1','h2','h3','h4','h5','h6'):
			elem.tag = 'h%d' % (int(elem.tag[1]) + current_app.config['PLUGIN_HEADERSHIFT_LEVEL'])
