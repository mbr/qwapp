#!/usr/bin/env python
# coding=utf8

from flask import Flask, render_template, abort, url_for
from flaskext.markdown import Markdown

from db import WikiDb

REPOSITORY_PATH = './wiki'
DEBUG = True
SECRET_KEY = 'development key'
PASSWORD = 'devpass'


app = Flask('mywiki')
app.config.from_object(__name__)

def make_wiki_link(name, base, end):
	return url_for('show_page', name = name)

md = Markdown(app, safe_mode = False,
                   extensions = ['wikilinks'],
                   extension_configs = {
                       'wikilinks': [('build_url', make_wiki_link)]
                   })

db = WikiDb(app.config['REPOSITORY_PATH'])


@app.route('/')
def index():
	page = db.get_special('index.markdown')
	return render_template('page.html', body = page, title = 'Welcome')


@app.route('/list/pages/')
def list_pages():
	return render_template('pagelist.html', pages = db.list_pages())



@app.route('/<name>/')
def show_page(name):
	page = db.get_page(name)
	if not page: abort(404)
	return render_template('page.html', body = page, title = name)


if '__main__' == __name__:
	app.run(use_debugger = True, use_reloader = True)
