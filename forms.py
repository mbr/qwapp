#!/usr/bin/env python
# coding=utf8

from flaskext.wtf import Form, TextField, Required, TextAreaField, SubmitField

class EditPageForm(Form):
	body = TextAreaField(u'Page contents', validators = [Required()])
	commit_msg = TextField(u'Commit message', validators = [Required()])
	preview = SubmitField(u'Preview')
	save = SubmitField(u'Save')
