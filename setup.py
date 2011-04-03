#!/usr/bin/env python
# coding=utf8

from distutils.core import setup

setup(name = 'qwapp',
      version = '0.1dev',
      description = 'A git-backed wiki WSGI app',
      author = 'Marc Brinkmann',
      url = 'https://github.com/qwapp',
      packages = ['qwapp', 'qwappplugin'],
      namespace_packages = ['qwappplugin'],
     )
