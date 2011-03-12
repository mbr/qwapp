#!/usr/bin/env python
# coding=utf8

from flask import Flask
import defconfig

app = Flask('qwapp')

# load a default config, and from envvar
app.config.from_object(defconfig)
app.config.from_envvar('QWAPP_CONFIG')

import qwapp.views
