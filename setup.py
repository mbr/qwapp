#!/usr/bin/env python
# coding=utf8

from distutils.core import setup

setup(name = 'qwapp',
      version = '0.1dev',
      description = 'A git-backed wiki WSGI app',
      author = 'Marc Brinkmann',
      url = 'https://github.com/qwapp',
      packages = ['qwapp', 'qwapp.mdx', 'qwapp.views', 'qwappplugin'],
      package_data = {'qwapp': ['static/css/*.css', 'templates/*.html']},
      namespace_packages = ['qwappplugin'],
      install_requires = ['flask', 'dulwich', 'flask', 'Flask-Cache', 'Flask-Markdown', 'Flask-WTF', 'blinker'],
      zip_safe=False,
     )
