#!/usr/bin/env python
# coding=utf8

from flaskext.wtf import Form, TextField, Required, TextAreaField, SubmitField, PasswordField

class EditPageForm(Form):
	body = TextAreaField(u'Page contents', validators = [Required()])
	commit_msg = TextField(u'Commit message', validators = [Required()], default = 'Minor edit.')
	preview = SubmitField(u'Preview')
	save = SubmitField(u'Save')


class LoginForm(Form):
	password = PasswordField(u'Password')
	login = SubmitField(u'Login')


class DeletePageForm(Form):
	delete_button = SubmitField(u'Yes, delete it!')
