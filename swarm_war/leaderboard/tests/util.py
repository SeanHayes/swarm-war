# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib.auth.models import User
from django.test import TestCase

class BaseTestCase(TestCase):
	def setUp(self):
		self.username = 'test_user'
		self.password = 'foobar'
		self.user = User.objects.create_user(self.username, 'test_user@example.com', self.password)
		self.user2 = User.objects.create_user('test_user2', 'test_user2@example.com', self.password)
		self.user3 = User.objects.create_user('test_user3', 'test_user3@example.com', self.password)
		self.user4 = User.objects.create_user('test_user4', 'test_user4@example.com', self.password)
		self.user5 = User.objects.create_user('test_user5', 'test_user52@example.com', self.password)
		self.user6 = User.objects.create_user('test_user6', 'test_user6@example.com', self.password)
		
		self.client.login(username=self.username, password=self.password)
		
		cp1 = self.user.coreprofile
		cp1.experience = 0
		cp1.save()
		cp2 = self.user2.coreprofile
		cp2.experience = 10
		cp2.save()
		cp3 = self.user2.coreprofile
		cp3.experience = 10
		cp3.save()
		cp4 = self.user2.coreprofile
		cp4.experience = 10
		cp4.save()
		cp5 = self.user2.coreprofile
		cp5.experience = 10
		cp5.save()
		cp6 = self.user2.coreprofile
		cp6.experience = 10
		cp6.save()
	
