#!/usr/bin/env python
# coding=utf8

from functools import wraps

from flask import Module, render_template, abort, url_for, redirect, session, current_app, request, abort

from ..db import FileNotFoundException
from .. import password, forms


class RenderPage(object):
	def __init__(self, title, body):
		self.title = title
		self.body = body


frontend = Module(__name__)

def require_login(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if current_app.config['PASSWORD_HASH']:
			if not 'logged_in' in session or not session['logged_in']:
				return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function


def cached(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		cache_key = 'view/%s' % request.path

		rv = current_app.cache.get(cache_key)
		if rv is None:
			rv = f(*args, **kwargs)
			current_app.cache.set(cache_key, rv)
		return rv

	return decorated_function


@frontend.route('/w/login/', methods = ('GET', 'POST'))
def login():
	form = forms.LoginForm()
	if form.validate_on_submit():
		if password.check_password(form.password.data, current_app.config['PASSWORD_HASH']):
			# set the login value
			session['logged_in'] = True
			session.permanent = True

			return redirect(url_for('show_special', name = 'index'))
	return render_template('loginform.html', form = form)


@frontend.route('/w/list-pages/')
@require_login
@cached
def list_pages():
	return render_template('pagelist.html', pages = current_app.db.list_pages())


@frontend.route('/')
@frontend.route('/s/<name>/')
@require_login
@cached
def show_special(name = 'index'):
	special_names = {
		'index': current_app.config['WIKI_NAME'],
	}

	try:
		body = current_app.db.get_special(name)
		page = RenderPage(special_names[name], body)
	except FileNotFoundException:
		return redirect(url_for('edit_special', name = name))

	return render_template('page.html', body = page.body, title = page.title, edit_link = url_for('edit_special', name = name))


@frontend.route('/s/<name>/edit/', methods = ('GET', 'POST'))
@require_login
def edit_special(name):
	try:
		page = current_app.db.get_special(name)
	except FileNotFoundException:
		page = None

	form = forms.EditPageForm(body = page)
	preview = None

	if form.validate_on_submit():
		if form.preview.data:
			preview = form.body.data
		else:
			current_app.db.update_special(name, form.body.data, form.commit_msg.data)

			# invalidate cache
			current_app.cache.delete('view/%s' % url_for('show_special', name = name))
			return redirect(url_for('show_special', name = name))

	return render_template('editpage.html', form = form, preview = preview)


@require_login
@frontend.route('/<name>/edit/', methods = ('GET', 'POST'))
def edit_page(name):
	try:
		page = current_app.db.get_page(name)
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
			current_app.db.update_page(name, form.body.data, form.commit_msg.data)

			# redirect to page view
			current_app.cache.delete('view/%s' % url_for('show_page', name = name))
			current_app.cache.delete('view/%s' % url_for('list_pages'))
			return redirect(url_for('show_page', name = name))

	return render_template('editpage.html', form = form, preview = preview)


@require_login
@frontend.route('/<name>/delete/', methods = ('GET', 'POST'))
def delete_page(name):
	try:
		page = current_app.db.get_page(name)
	except FileNotFoundException:
		abort(404)

	form = forms.DeletePageForm()

	if form.validate_on_submit():
		current_app.db.delete_page(name)

		# invalidate cache
		current_app.cache.delete('view/%s' % url_for('show_page', name = name))
		current_app.cache.delete('view/%s' % url_for('list_pages'))
		return redirect(url_for('show_special', name = 'index'))

	return render_template('deletepage.html', form = form, title = name)


@frontend.route('/<name>/')
@require_login
@cached
def show_page(name):
	try:
		body = current_app.db.get_page(name)
		page = RenderPage(name, body)
	except FileNotFoundException:
		return redirect(url_for('edit_page', name = name))
	return render_template('page.html', body = page.body, title = page.title, edit_link = url_for('edit_page', name = name), delete_link = url_for('delete_page', name = name))
