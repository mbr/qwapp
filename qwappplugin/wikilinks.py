#!/usr/bin/env python
# coding=utf8

import re
import uuid

from flask import url_for, current_app

from qwapp.plugin import Plugin, ET

plugin = Plugin('Wiki-style links', author = 'Marc Brinkmann', description = 'Adds support for [[WikipediaStyle]] links.', version = (0,1))

WIKI_EXP = r'\[\[(.*?)(?:\|(.*?))?\]\]([^\s.:;!?"*]*)'
WIKI_RE = re.compile(WIKI_EXP)

@plugin.on_signal('page-preprocess')
def substitute_ids(page):
	page.wikilinks = {}

	def _on_wikilink(m):
		label = (m.group(2) or m.group(1)) + m.group(3)
		target = m.group(1)
		link_id = uuid.uuid4().hex
		page.wikilinks[link_id] = (label, target)

		return link_id

	page.body = WIKI_RE.sub(_on_wikilink, page.body)

@plugin.on_signal('page-postmarkdown')
def insert_wikilink_tags(page):
	for key in page.wikilinks.iterkeys():
		page.body = page.body.replace(key, '<wikilink id="%s"/>' % key)

@plugin.on_signal('page-treeprocess')
def transform_links(page):
	for elem in page.body.getiterator('wikilink'):
		label, taget = page.wikilinks[elem.get('id')]
		# do not clear element - this would remove the tail
		elem.tag = 'a'
		elem.text = label
		del elem.attrib['id']
		elem.set('title', label)
		elem.set('href', url_for('show_page', name = label))
		class_ = 'qwapp_link'
		if not current_app.db.has_page(label): class_ += ' qwapp_new_page'
		elem.set('class', class_)
