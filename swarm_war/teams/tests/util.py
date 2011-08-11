# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase

#App imports
from ..models import Team

class BaseTestCase(TestCase):
	def setUp(self):
		self.user1name = 'test_user'
		self.password = 'foobar'
		self.user1 = User.objects.create_user(self.user1name, 'test_user@example.com', self.password)
		self.user2 = User.objects.create_user('baddie', 'baddie@example.com', 'Teletubies')
		self.team1 = Team(name='The Warriors')
		self.team2 = Team(name='Power Rangers')
		
		self.client.login(username=self.user1name, password=self.password)
	
	def tearDown(self):
		#FIXME: dqc doesn't intercept db destruction or rollback
		cache.clear()
