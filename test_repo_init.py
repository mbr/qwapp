#!/usr/bin/env python
# coding=utf8

import sys
from qwapp.db import WikiDb

w = WikiDb(sys.argv[1])
w.reset_repo()
