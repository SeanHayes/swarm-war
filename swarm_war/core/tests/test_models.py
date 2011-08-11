# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
from datetime import datetime
#import ipdb
import urllib

#Django imports
from django.conf import settings

#App imports
from ..models import FacebookRequest, CoreProfile

#Test imports
from util import BaseTestCase

class CoreProfileTestCase(BaseTestCase):
	def test_get_experience_level_with_iterator(self):
		old_DW_CORE_XP_LEVEL_ITERATOR = settings.DW_CORE_XP_LEVEL_ITERATOR
		settings.DW_CORE_XP_LEVEL_ITERATOR = lambda: [(10, 10), (10, 20), (10, 30),]
		
		cp = self.user.coreprofile
		
		cp.experience = 0
		self.assertEqual(cp.get_experience_level(), 1)
		cp.experience = 5
		self.assertEqual(cp.get_experience_level(), 1)
		cp.experience = 10
		self.assertEqual(cp.get_experience_level(), 2)
		cp.experience = 19
		self.assertEqual(cp.get_experience_level(), 2)
		cp.experience = 20
		self.assertEqual(cp.get_experience_level(), 3)
		cp.experience = 29
		self.assertEqual(cp.get_experience_level(), 3)
		cp.experience = 30
		self.assertEqual(cp.get_experience_level(), 4)
		
		
		cp.experience = 100
		self.assertEqual(cp.get_experience_level(), 10)
		cp.experience = 101
		self.assertEqual(cp.get_experience_level(), 11)
		cp.experience = 111
		self.assertEqual(cp.get_experience_level(), 11)
		cp.experience = 120
		self.assertEqual(cp.get_experience_level(), 12)
		
		
		settings.DW_CORE_XP_LEVEL_ITERATOR = old_DW_CORE_XP_LEVEL_ITERATOR
