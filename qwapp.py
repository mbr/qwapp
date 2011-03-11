#!/usr/bin/env python
# coding=utf8

from functools import wraps

from flask import Flask, render_template, abort, url_for, redirect, session
from flaskext.markdown import Markdown

from db import WikiDb, FileNotFoundException
import forms

import defconfig
import password


def make_wiki_link(name, base, end):
	return url_for('show_page', name = name)


app = Flask('qwapp')

# load a default config
app.config.from_object(defconfig)

# load user config from an envvar
app.config.from_envvar('QWAPP_CONFIG')

md = Markdown(app, safe_mode = False,
				   extensions = ['wikilinks'],
				   extension_configs = {
					   'wikilinks': [('build_url', make_wiki_link)]
				   })


db = WikiDb(app.config['REPOSITORY_PATH'])

special_names = {
	'index': 'Welcome',
}


def require_login(f):
	@wraps(f)
	def decorator(*args, **kwargs):
		if app.config['PASSWORD_HASH']:
			if not 'logged_in' in session or not session['logged_in']:
				return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorator


# login handling
@app.route('/w/login/', methods = ('GET', 'POST'))
def login():
	form = forms.LoginForm()
	if form.validate_on_submit():
		if password.check_password(form.password.data, app.config['PASSWORD_HASH']):
			# set the login value
			session['logged_in'] = True
			session.permanent = True

			return redirect(url_for('show_special', name = 'index'))
	return render_template('loginform.html', form = form)


@app.route('/w/list-pages/')
@require_login
def list_pages():
	return render_template('pagelist.html', pages = db.list_pages())


@app.route('/')
@app.route('/s/<name>/')
@require_login
def show_special(name = 'index'):
	try:
		page = db.get_special(name)
	except FileNotFoundException:
		redirect(url_for('edit_special', name = name))
	return render_template('page.html', body = page, title = special_names[name], edit_link = url_for('edit_special', name = name))


@app.route('/s/<name>/edit/', methods = ('GET', 'POST'))
@require_login
def edit_special(name):
	try:
		page = db.get_special(name)
	except FileNotFoundException:
		page = None

	form = forms.EditPageForm(body = page)
	preview = None

	if form.validate_on_submit():
		if form.preview.data:
			preview = form.body.data
		else:
			db.update_special(name, form.body.data, form.commit_msg.data)

			return redirect(url_for('show_special', name = name))

	return render_template('editpage.html', form = form, preview = preview)


@require_login
@app.route('/<name>/edit/', methods = ('GET', 'POST'))
def edit_page(name):
	try:
		page = db.get_page(name)
	except FileNotFoundException:
		page = None

	form = forms.EditPageForm(body = page)
	preview = None

	if form.validate_on_submit():
		if form.preview.data:
			# simply display preview
			preview = form.body.data
		else:
			# save the new page
			db.update_page(name, form.body.data, form.commit_msg.data)

			# redirect to page view
			return redirect(url_for('show_page', name = name))

	return render_template('editpage.html', form = form, preview = preview)


@app.route('/<name>/')
@require_login
def show_page(name):
	try:
		page = db.get_page(name)
	except FileNotFoundException:
		return redirect(url_for('edit_page', name = name))
	return render_template('page.html', body = page, title = name, edit_link = url_for('edit_page', name = name))


if '__main__' == __name__:
	app.run(use_debugger = True, use_reloader = True)
