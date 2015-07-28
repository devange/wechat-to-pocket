import datetime
from django.db import models

class Log(models.Model):
	log = models.CharField(max_length=255)
	msg = models.CharField(max_length=255)
	pubdate = models.DateTimeField(default=datetime.datetime.now)

class User(models.Model):
	wechat_user = models.CharField(max_length=40)
	request_token = models.CharField(max_length=255)
	pubdate = models.DateTimeField(default=datetime.datetime.now)

class User2(models.Model):
	wechat_user = models.CharField(max_length=40)
	pocket_user = models.CharField(max_length=40)
	access_token = models.CharField(max_length=255)
	pubdate = models.DateTimeField(default=datetime.datetime.now)

class Saveitem(models.Model):
	wechat_user = models.CharField(max_length=40)
	pocket_user = models.CharField(max_length=40)
	title = models.CharField(max_length=40)
	url = models.CharField(max_length=255)
	status = models.IntegerField()
	log = models.CharField()
	pubdate = models.DateTimeField(default=datetime.datetime.now)

class Chat(models.Model):
	wechat_user = models.CharField(max_length=40)
	pocket_user = models.CharField(max_length=40)
	chat = models.CharField()
	pubdate = models.DateTimeField(default=datetime.datetime.now)
