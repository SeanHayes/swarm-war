# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase

#App imports
from ..models import Listing

class BaseTestCase(TestCase):
	def setUp(self):
		self.username = 'test_user'
		self.password = 'foobar'
		self.user = User.objects.create_user(self.username, 'test_user@example.com', self.password)
		self.l1 = Listing(num_game_credits=10, num_fb_credits=10)
		self.l2 = Listing(num_game_credits=20, num_fb_credits=15, title="Special deal!", description="Bulk discount, extra 5 credits!")
		self.client.login(username=self.username, password=self.password)
	
	def tearDown(self):
		#FIXME: dqc doesn't intercept db destruction or rollback
		cache.clear()
