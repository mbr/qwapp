#!/usr/bin/env python
# coding=utf8

"""Shifts HTML headers "downwards", i.e. with a shift of 2,
<h1> becomes <h3>, <h2> becomes <h4> and so on."""

import markdown

class HeaderShiftProcessor(markdown.treeprocessors.Treeprocessor):
	def __init__(self, amount, *args, **kwargs):
		markdown.treeprocessors.Treeprocessor(*args, **kwargs)
		self.amount = amount

	def run(self, root):
		for c in root.getchildren():
			if len(c.tag) == 2 and c.tag[0].lower() == 'h' and c.tag[1].isdigit() :
				c.tag = '%s%d' % (c.tag[0], max(0, min(6, int(c.tag[1]) + self.amount))) # modifiy in place
			self.run(c)
		return root


class HeadershiftExtension(markdown.Extension):
	def __init__(self, configs):
		self.config = {
			'shift_amount': 2,
		}

		for key, value in configs:
			self.setConfig(key, value)

	def extendMarkdown(self, md, md_globals):
		md.treeprocessors.add('headershift', HeaderShiftProcessor(self.config['shift_amount'], md), '_end')


def makeExtension(configs = None):
	return HeadershiftExtension(configs = configs)
