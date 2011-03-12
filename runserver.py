#!/usr/bin/env python
# coding=utf8

from qwapp import create_app

app = create_app()
app.run(use_debugger = True, use_reloader = True)
