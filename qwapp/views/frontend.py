#!/usr/bin/env python
# coding=utf8

from functools import wraps
from uuid import uuid4
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

from flask import Module, render_template, abort, url_for, redirect, session, current_app, request, abort
import markdown2

from ..db import FileNotFoundException
from .. import password, forms
from ..plugin import make_block_expression


class RenderPage(object):
	def __init__(self, title, body):
		self.title = title
		self.body = body
		self.blocks = {}

	def extract_blocks(self, blockname):
		self.blocks[blockname] = []
		exp = make_block_expression(blockname)
		self.body = exp.sub(self._handle_block_match, self.body)

	def _handle_block_match(self, m):
		id = uuid4()
		self.blocks[m.group(1)].append((id.hex, m.group(2)))
		return id.hex

	def process(self):
		current_app.plugin_signals['page-preprocess'].send(self)
		self.body = u'<div class="pagebody">%s</div>' % markdown2.markdown(self.body)
		current_app.plugin_signals['page-postmarkdown'].send(self)

		# convert body to XML tree
		self.body = ET.XML(self.body.encode('utf-8'))
		current_app.plugin_signals['page-treeprocess'].send(self)

		# output final result (before postprocessing)
		self.body = ET.tostring(self.body, 'utf-8').decode('utf-8')
		current_app.plugin_signals['page-postprocess'].send(self)


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
		current_app.plugin_signals['special-loaded'].send(current_app._get_current_object(), page = page)
		page.process()
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
	preview_body = None

	if form.validate_on_submit():
		if form.preview.data:
			preview = RenderPage('Preview', form.body.data)
			preview.process()
			preview_body = preview.body
		else:
			current_app.db.update_special(name, form.body.data, form.commit_msg.data)

			# invalidate cache
			current_app.cache.delete('view/%s' % url_for('show_special', name = name))
			return redirect(url_for('show_special', name = name))

	return render_template('editpage.html', form = form, preview = preview_body)


@require_login
@frontend.route('/<name>/edit/', methods = ('GET', 'POST'))
def edit_page(name):
	# FIXME: invalidate caches on edit, so that link coloring works as expected
	try:
		page = current_app.db.get_page(name)
	except FileNotFoundException:
		page = None

	form = forms.EditPageForm(body = page)
	preview_body = None

	if form.validate_on_submit():
		if form.preview.data:
			# simply display preview
			preview = RenderPage('Preview', form.body.data)
			preview.process()
			preview_body = preview.body
		else:
			# save the new page
			current_app.db.update_page(name, form.body.data, form.commit_msg.data)

			# redirect to page view
			current_app.cache.delete('view/%s' % url_for('show_page', name = name))
			current_app.cache.delete('view/%s' % url_for('list_pages'))
			return redirect(url_for('show_page', name = name))

	return render_template('editpage.html', form = form, preview = preview_body)


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
		current_app.plugin_signals['page-loaded'].send(current_app._get_current_object(), page = page)
		page.process()
	except FileNotFoundException:
		return redirect(url_for('edit_page', name = name))
	return render_template('page.html', body = page.body, title = page.title, edit_link = url_for('edit_page', name = name), delete_link = url_for('delete_page', name = name))
