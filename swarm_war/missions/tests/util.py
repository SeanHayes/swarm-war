# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.core.cache import cache
from django.test import TestCase

class BaseTestCase(TestCase):
	
	def tearDown(self):
		#FIXME: dqc doesn't intercept db destruction or rollback
		cache.clear()
