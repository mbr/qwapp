#!/usr/bin/env python
# coding=utf8

from flask import Flask, g, url_for
from flaskext.cache import Cache
import flask.signals
from flaskext.markdown import Markdown
from qwapp.views.frontend import frontend

import defaults

from db import WikiDb
from mdx.mdx_headershift import HeadershiftExtension
from mdx.mdx_wikilinks2 import WikiLinks2Extension

def create_app(configuration_file = None):
	app = Flask(__name__)
	app.plugin_signals = flask.signals.Namespace()

	# load a default config, and from configuration file
	app.config.from_object(defaults)
	if configuration_file:
		app.config.from_pyfile(configuration_file)

	app.db = WikiDb(app.config['REPOSITORY_PATH'])

	app.md = Markdown(app, safe_mode = False, extensions = [
		HeadershiftExtension({'shift_amount': 1}.items()),
		WikiLinks2Extension({'build_href': lambda target, label: url_for('show_page', name = target)}.items()),
	])
	app.cache = Cache(app)

	app.register_module(frontend)

	# load plugins
	for plugin_name in app.config['PLUGINS']:
		import_name = 'qwappplugin.%s' % plugin_name

		qwappplugin = __import__('qwappplugin.%s' % plugin_name)
		plugin_module = getattr(qwappplugin, plugin_name)

		plugin_module.plugin.register_app(app)

	return app
