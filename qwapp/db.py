#!/usr/bin/env python
# coding=utf8

import email.utils
import os
import socket
import stat
import time

from dulwich.repo import Repo
from dulwich.objects import Blob, Commit, Tree, parse_timezone

# regular file, default permissions of rw-r--r--
_git_default_file_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH


def _walk_git_repo_tree(repo, tree, path):
	for part in path.encode('utf-8').split('/'):
		mode, sha = tree[part]
		if mode & stat.S_IFDIR:
			tree = repo[sha]
		else:
			return repo[sha]
	return repo[sha]

class WikiDbException(Exception): pass
class FileNotFoundException(WikiDbException): pass

class WikiDb(object):
	def __init__(self, repopath, head = 'refs/heads/master'):
		self.repo = Repo(repopath)
		self.head = head

		if not self.head in self.repo.refs:
			self.reset_repo()

	def reset_repo(self):
		# ensure head exists
			tree = Tree()

			commit = Commit()
			commit.tree = tree.id
			commit.author = commit.committer = self.wiki_user
			commit.commit_time = commit.author_time = int(time.time())
			commit.commit_timezone = commit.author_timezone = parse_timezone(time.timezone)[0]
			commit.encoding = 'UTF-8'
			commit.message = u'Automatic initalization by qwapp.'.encode('utf-8')

			# store all objects
			self.repo.object_store.add_object(tree)
			self.repo.object_store.add_object(commit)

			# update the branch
			self.repo.refs[self.head] = commit.id

	@property
	def current_commit(self):
		head = self.repo.refs[self.head]
		return self.repo[head]

	@property
	def current_tree(self):
		return self.repo[self.current_commit.tree]

	@property
	def wiki_user(self):
		try:
			user = os.getlogin()
		except OSError:
			user = 'wiki.unknown'
		addr = '%s@%s' % (user, socket.gethostname())

		return email.utils.formataddr((user, addr))

	def delete_file(self, subdir, filename, commit_msg):
		try:
			subdir_tree = _walk_git_repo_tree(self.repo, self.current_tree, subdir)
		except KeyError:
			raise FileNotFoundException('No subdir named %r' % subdir)
		if not filename in subdir_tree: raise FileNotFoundException('%r not in %s' % (filename, subdir))
		del subdir_tree[filename]

		# create new root tree
		tree = self.current_tree
		tree.add(stat.S_IFDIR, subdir, subdir_tree.id)

		# create commit
		# FIXME: factor this out!
		commit = Commit()
		commit.parents = [self.current_commit.id]
		commit.tree = tree.id
		commit.author = commit.committer = self.wiki_user
		commit.commit_time =  commit.author_time = int(time.time())
		commit.commit_timezone = commit.author_timezone = parse_timezone(time.timezone)[0]
		commit.encoding = 'UTF-8'
		commit.message = commit_msg.encode('utf-8')

		# store all objects
		self.repo.object_store.add_object(subdir_tree)
		self.repo.object_store.add_object(tree)
		self.repo.object_store.add_object(commit)

		# update the branch
		self.repo.refs[self.head] = commit.id

	def delete_page(self, name):
		return self.delete_file('pages', ('%s.markdown' % name).encode('utf-8'), u'Deleted page "%s"' % name)

	def get_file(self, path):
		try:
			return _walk_git_repo_tree(self.repo, self.current_tree, path).as_raw_string()
		except KeyError: raise FileNotFoundException('could not find %r' % path)

	def get_page(self, name):
		return self.get_file('pages/%s.markdown' % name).decode('utf-8')

	def get_special(self, name):
		return self.get_file('special/%s.markdown' % name).decode('utf-8')

	def list_pages(self):
		mode, pages_sha = self.current_tree['pages']
		for name, mode, sha in self.repo[pages_sha].iteritems():
			yield name[:-len('.markdown')].decode('utf-8')

	def update_page(self, name, data, commit_msg):
		self._update_file(name, 'pages', '%s.markdown' % name.encode('utf-8'), data, commit_msg)

	def update_special(self, name, data, commit_msg):
		self._update_file(name, 'special', '%s.markdown' % name.encode('utf-8'), data, commit_msg)

	def _update_file(self, name, subdir, filename, data, commit_msg):
		# first, create a new blob for the data
		blob = Blob.from_string(data.encode('utf-8'))

		# fetch the old tree object, add new page
		try:
			subdir_tree = _walk_git_repo_tree(self.repo, self.current_tree, subdir)
		except KeyError:
			# we need to create the subdir_tree as well, since it does not exist
			# yet
			subdir_tree = Tree()
		subdir_tree.add(_git_default_file_mode, filename, blob.id)

		# create new root tree
		tree = self.current_tree
		tree.add(stat.S_IFDIR, subdir, subdir_tree.id)

		# create commit
		commit = Commit()
		commit.parents = [self.current_commit.id]
		commit.tree = tree.id
		commit.author = commit.committer = self.wiki_user
		commit.commit_time =  commit.author_time = int(time.time())
		commit.commit_timezone = commit.author_timezone = parse_timezone(time.timezone)[0]
		commit.encoding = 'UTF-8'
		commit.message = commit_msg.encode('utf-8')

		# store all objects
		self.repo.object_store.add_object(blob)
		self.repo.object_store.add_object(subdir_tree)
		self.repo.object_store.add_object(tree)
		self.repo.object_store.add_object(commit)

		# update the branch
		self.repo.refs[self.head] = commit.id
