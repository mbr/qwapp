#!/usr/bin/env python
# coding=utf8

import email.utils
import os
import socket
import stat
import time

from dulwich.repo import Repo
from dulwich.objects import Blob, Commit, parse_timezone


def _walk_git_repo_tree(repo, tree, path):
	for part in path.split('/'):
		mode, sha = tree[part]
		if mode & stat.S_IFDIR:
			tree = repo[sha]
		else:
			return repo[sha]
	return repo[sha]

class WikiDb(object):
	def __init__(self, repopath, head = 'refs/heads/master'):
		self.repo = Repo(repopath)
		self.head = head

	@property
	def current_commit(self):
		head = self.repo.refs[self.head]
		return self.repo[head]

	@property
	def current_tree(self):
		return self.repo[self.current_commit.tree]

	def get_file(self, path):
		try:
			return _walk_git_repo_tree(self.repo, self.current_tree, path).as_raw_string()
		except KeyError: return None

	def get_page(self, name):
		return self.get_file('pages/%s.markdown' % name)

	def get_special(self, name):
		return self.get_file('special/index.markdown')

	def list_pages(self):
		mode, pages_sha = self.current_tree['pages']
		for name, mode, sha in self.repo[pages_sha].iteritems():
			yield name[:-len('.markdown')]

	def update_page(self, name, data, commit_msg):
		# first, create a new blob for the data
		blob = Blob.from_string(data.encode('utf-8'))

		# regular file, default permissions of rw-r--r--
		mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH

		# fetch the old tree object, add new page
		pages_tree = _walk_git_repo_tree(self.repo, self.current_tree, 'pages')
		pages_tree.add(mode, '%s.markdown' % name.encode('utf-8'), blob.id)

		# create new root tree
		tree = self.current_tree
		tree.add(stat.S_IFDIR, 'pages', pages_tree.id)

		# create commit
		user = os.getlogin()
		addr = '%s@%s' % (user, socket.gethostname())

		commit = Commit()
		commit.parents = [self.current_commit.id]
		commit.tree = tree.id
		commit.author = commit.committer = email.utils.formataddr((user, addr))
		commit.commit_time =  commit.author_time = int(time.time())
		commit.commit_timezone = commit.author_timezone = parse_timezone(time.timezone)[0]
		commit.encoding = 'UTF-8'
		commit.message = commit_msg.encode('utf-8')

		# store all objects
		self.repo.object_store.add_object(blob)
		self.repo.object_store.add_object(pages_tree)
		self.repo.object_store.add_object(tree)
		self.repo.object_store.add_object(commit)

		# update the branch
		self.repo.refs[self.head] = commit.id
