# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import pdb

#App imports
from test_managers import *
from test_models import *
from test_tasks import *
from test_urls import *
from util import BaseTestCase

__test__ = {
	'test_managers': [test_managers],
	'test_models': [test_models],
	'test_tasks': [test_tasks],
	'test_urls': [test_urls],
}

class LevelUpTestCase(BaseTestCase):
	def test_level_up_by_user(self):
		"Ensure that a user is notified when leveling up, but only once."
		profile = CoreProfile.objects.get(user=self.user)
		self.assertEqual(profile.experience, 0)
		self.assertEqual(profile.get_experience_level(), 1)
		self.assertEqual(profile.leveled_up, False)
		
		profile.experience = 10
		profile.save()
		
		#ensure XP increased
		profile = CoreProfile.objects.get(user=self.user)
		self.assertEqual(profile.experience, 10)
		self.assertEqual(profile.get_experience_level(), 2)
		self.assertEqual(profile.leveled_up, True)
		
		leveled_up_text = 'Leveled Up!'
		
		response = self.client.get('/')
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, leveled_up_text)
		
		profile = CoreProfile.objects.get(user=self.user)
		self.assertEqual(profile.experience, 10)
		self.assertEqual(profile.get_experience_level(), 2)
		self.assertEqual(profile.leveled_up, False)
		
		response = self.client.get('/')
		
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, leveled_up_text)
