#!/usr/bin/env python
# coding=utf8

import sys

from qwapp import create_app

if len(sys.argv) == 2:
	print 'using configuration file',sys.argv[1]
	app = create_app(sys.argv[1])
else:
	app = create_app()

app.run(use_debugger = True, use_reloader = True)
