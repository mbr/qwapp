#!/usr/bin/env python
# coding=utf8

import markdown

class WikiLinks2Pattern(markdown.inlinepatterns.Pattern):
	def __init__(self, ext, md):
		self.ext = ext
		markdown.inlinepatterns.Pattern.__init__(self, ext.WIKI_RE, md)

		self.build_link = ext.getConfig('build_link')
		self.build_href = ext.getConfig('build_href')
		self.link_class = ext.getConfig('link_class')

	def handleMatch(self, m):
		label = (m.group(3) or m.group(2)) + m.group(4)
		target = m.group(2)
		href = self.build_href(target, label)
		a = self.build_link(label, href, None, self.link_class)
		return a


def build_link(label, href, title = None, class_ = None):
	e = markdown.etree.Element('a')
	if class_: e.set('class', class_)
	e.text = label
	e.set('href',href)
	e.set('title',title or label)
	return e


def build_href(target, label):
	return '/LINK:' + target


class Wikilinks2Extension(markdown.Extension):
	WIKI_RE = r'\[\[(.*?)(?:\|(.*?))?\]\]([^\s.:;!?"]*)'

	def __init__(self, configs):
		self.config = {
			'build_href': [build_href, 'A callback that given target and label, constructs a URL'],
			'build_link': [build_link, 'A callback that constructs a link element using ElementTree from the label, href, title and class attributes.'],
			'link_exp': [self.WIKI_RE, 'Regular expression used to find Wiki-links.'],
			'link_class': ['wikilink', 'The class applied to all links.'],
		}

		for key, value in configs:
			self.setConfig(key, value)

	def extendMarkdown(self, md, md_globals):
		md.inlinePatterns.add('wikilinks2', WikiLinks2Pattern(self, md), '_begin')


def makeExtension(configs = None):
	return Wikilinks2Extension(configs = configs)
