#!/usr/bin/env python
# coding=utf8

from dulwich.repo import Repo
import stat

def _walk_git_repo_tree(repo, tree, path):
	for part in path.split('/'):
		mode, sha = tree[part]
		if mode & stat.S_IFDIR:
			tree = repo[sha]
		else:
			return repo[sha]

class WikiDb(object):
	def __init__(self, repopath, head = 'refs/heads/master'):
		self.repo = Repo(repopath)
		self.head = head

	@property
	def current_commit(self):
		head = self.repo.refs[self.head]
		return self.repo[head]

	def get_file(self, path):
		# get head sha
		tree = self.repo[self.current_commit.tree]
		try:
			return _walk_git_repo_tree(self.repo, tree, path).as_raw_string()
		except KeyError: return None

	def get_page(self, name):
		return self.get_file('pages/%s.markdown' % name)

	def get_special(self, name):
		return self.get_file('special/index.markdown')

	def list_pages(self):
		tree = self.repo[self.current_commit.tree]

		mode, pages_sha = tree['pages']
		for name, mode, sha in self.repo[pages_sha].iteritems():
			yield name[:-len('.markdown')]
