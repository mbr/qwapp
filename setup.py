#!/usr/bin/env python
# coding=utf8

from distutils.core import setup

setup(name = 'qwapp',
      version = '0.1dev',
      description = 'A git-backed wiki WSGI app',
      author = 'Marc Brinkmann',
      url = 'https://github.com/qwapp',
      packages = ['qwapp', 'qwapp.views', 'qwappplugin'],
      package_data = {'qwapp': ['static/css/*.css', 'templates/*.html']},
      namespace_packages = ['qwappplugin'],
      install_requires = ['flask', 'dulwich', 'markdown2', 'Flask-Cache', 'Flask-WTF', 'blinker'],
      zip_safe=False,
     )
