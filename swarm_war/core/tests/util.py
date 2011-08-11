# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase

#App imports
from ..models import Item
from swarm_war.missions.models import Mission, Area

class BaseTestCase(TestCase):
	def setUp(self):
		self.username = 'test_user'
		self.password = 'foobar'
		self.user = User.objects.create_user(self.username, 'test_user@example.com', self.password)
		self.opponent = User.objects.create_user('baddie', 'baddie@example.com', 'Teletubies')
		self.i1 = Item(
			name='Type II Phaser',
			attack=10,
		)
		self.i2 = Item(
			name='Phaser Rifle',
			attack=20,
		)
		self.i3 = Item(
			name='Bat\'leth',
			attack=10,
		)
		self.i4 = Item(
			name='Disruptor',
			attack=50,
		)
		#These really shouldn't be involved in core tests, but creating a mock
		#Item subclass just for testing is problematic.
		self.a1 = Area(name="Outer Space")
		self.m1 = Mission(name='Search and Destroy')
		self.client.login(username=self.username, password=self.password)
	
	def tearDown(self):
		#FIXME: dqc doesn't intercept db destruction or rollback
		cache.clear()
