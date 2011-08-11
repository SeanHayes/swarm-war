# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
#import ipdb

#Django imports
from django.conf import settings
from django.core.urlresolvers import reverse

#App imports
from ..views import get_player_leaderboard
from util import BaseTestCase

class IndexTestCase(BaseTestCase):
	def test_page_loads(self):
		old_DW_LEADERBOARD_ENABLE_CATEGORY_PAGES = settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES
		settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES = True
		old_DW_LEADERBOARD_NUM_TOP_USERS = settings.DW_LEADERBOARD_NUM_TOP_USERS
		settings.DW_LEADERBOARD_NUM_TOP_USERS = 5
		
		
		response = self.client.get(reverse('leaderboard_index'))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, reverse('leaderboard_view', args=['Most Experience']))
		
		settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES = old_DW_LEADERBOARD_ENABLE_CATEGORY_PAGES
		settings.DW_LEADERBOARD_NUM_TOP_USERS = old_DW_LEADERBOARD_NUM_TOP_USERS
	
	def test_page_loads_no_category_pages(self):
		old_DW_LEADERBOARD_ENABLE_CATEGORY_PAGES = settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES
		settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES = False
		old_DW_LEADERBOARD_NUM_TOP_USERS = settings.DW_LEADERBOARD_NUM_TOP_USERS
		settings.DW_LEADERBOARD_NUM_TOP_USERS = 5
		
		response = self.client.get(reverse('leaderboard_index'))
		
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, reverse('leaderboard_view', args=['Most Experience']))
		
		settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES = old_DW_LEADERBOARD_ENABLE_CATEGORY_PAGES
		settings.DW_LEADERBOARD_NUM_TOP_USERS = old_DW_LEADERBOARD_NUM_TOP_USERS
	

class ViewTestCase(BaseTestCase):
	def test_page_loads(self):
		old_val = settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES
		settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES = True
		
		response = self.client.get(reverse('leaderboard_view', args=['Most Experience']))
		
		self.assertEqual(response.status_code, 200)
		
		settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES = old_val
	
	
	def test_page_loads_no_category_pages(self):
		old_val = settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES
		settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES = False
		
		response = self.client.get(reverse('leaderboard_view', args=['Most Experience']))
		
		self.assertEqual(response.status_code, 404)
		
		settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES = old_val
