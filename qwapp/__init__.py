#!/usr/bin/env python
# coding=utf8

from flask import Flask, g, url_for
from flaskext.cache import Cache
from blinker import Signal
from qwapp.views.frontend import frontend

import defaults

from db import WikiDb

def create_app(configuration_file = None):
	app = Flask(__name__)
	app.plugins = []

	# cannot use namespace here, weak signals will disappear
	app.plugin_signals = {
		'plugin-loaded': Signal(),
		'page-loaded': Signal(),
		'special-loaded': Signal(),
	}

	# load a default config, and from configuration file
	app.config.from_object(defaults)
	if configuration_file:
		app.config.from_pyfile(configuration_file)

	app.db = WikiDb(app.config['REPOSITORY_PATH'])
	app.cache = Cache(app)

	app.register_module(frontend)

	# load plugins
	for plugin_name in app.config['PLUGINS']:
		import_name = 'qwappplugin.%s' % plugin_name

		qwappplugin = __import__('qwappplugin.%s' % plugin_name)
		plugin_module = getattr(qwappplugin, plugin_name)
		app.logger.debug('loading plugin %s' % plugin_module.plugin.version_string)

		plugin_module.plugin.register_app(app)

	return app
