#!/usr/bin/env python
# coding=utf8

import os
from hashlib import sha256

def hash_password(password, salt = None, iterations = 1000):
	if not salt: salt = sha256(os.urandom(256)).hexdigest()

	h = password
	for i in xrange(0,iterations):
		h = sha256(salt + h).hexdigest()
	return salt + h


def check_password(password, pwdata):
	digest_len = 64
	# sha256 digestsize is 32 bytes
	salt = pwdata[:digest_len]
	pwhash = pwdata[digest_len:]
	return hash_password(password, salt) == pwdata

if '__main__' == __name__:
	import sys

	print hash_password(sys.argv[1])
