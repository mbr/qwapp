#!/usr/bin/env python
# coding=utf8

from flask import Flask, g, url_for
from flaskext.markdown import Markdown
from flaskext.cache import Cache
from qwapp.views.frontend import frontend

import defaults

from db import WikiDb

def create_app(configuration_file = None):
	app = Flask(__name__)

	# load a default config, and from configuration file
	app.config.from_object(defaults)
	if configuration_file:
		app.config.from_file(configuration_file)

	app.db = WikiDb(app.config['REPOSITORY_PATH'])
	app.md = Markdown(app, safe_mode = False, extensions = ['wikilinks'], extension_configs = { 'wikilinks': [('build_url', lambda name, base, end: url_for('show_page', name = name))] })
	app.cache = Cache(app)

	app.register_module(frontend)

	return app
