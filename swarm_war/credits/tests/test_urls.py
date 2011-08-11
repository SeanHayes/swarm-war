# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import pdb

#Django imports
from django.core.urlresolvers import reverse

#App imports
from util import BaseTestCase

class IndexTestCase(BaseTestCase):
	def test_empty(self):
		response = self.client.get(reverse('credits_index'))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "There are no listings.")
		self.assertNotContains(response, self.l1.get_title())
		self.assertNotContains(response, self.l2.get_title())
	
	def test_non_empty(self):
		self.l1.save()
		
		response = self.client.get(reverse('credits_index'))
		
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, "There are no listings.")
		self.assertContains(response, self.l1.get_title())
		self.assertNotContains(response, self.l2.get_title())
