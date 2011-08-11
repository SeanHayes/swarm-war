# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase

#App imports
from ..models import Collection, CollectionItem

class BaseTestCase(TestCase):
	def setUp(self):
		self.username = 'test_user'
		self.password = 'foobar'
		self.user = User.objects.create_user(self.username, 'test_user@example.com', self.password)
		
		self.client.login(username=self.username, password=self.password)
	
	def tearDown(self):
		#FIXME: dqc doesn't intercept db destruction or rollback
		cache.clear()
