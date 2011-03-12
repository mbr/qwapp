#!/usr/bin/env python
# coding=utf8

from flask import Flask, g, url_for
from flaskext.markdown import Markdown
from flaskext.cache import Cache
from qwapp.views.frontend import frontend
import defconfig

from db import WikiDb

def create_app():
	app = Flask(__name__)

	# load a default config, and from envvar
	app.config.from_object(defconfig)
	#app.config.from_envvar('QWAPP_CONFIG')

	app.db = WikiDb(app.config['REPOSITORY_PATH'])
	app.md = Markdown(app, safe_mode = False, extensions = ['wikilinks'], extension_configs = { 'wikilinks': [('build_url', lambda name, base, end: url_for('show_page', name = name))] })
	app.cache = Cache(app)

	app.register_module(frontend)

	return app
