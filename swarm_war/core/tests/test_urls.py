# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
from datetime import datetime
#import ipdb
import urllib

#Django imports
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.html import escape

#App imports
from ..models import FacebookRequest, CoreProfile

#Test imports
from util import BaseTestCase

class CanvasTestCase(BaseTestCase):
	def test_accept_request(self):
		#NOTE: Facebook doesn't use normal parameter conventions ("?request_ids=123,456" instead of "?request_ids=123&request_ids=456")
		request_id = '123456'
		fbr = FacebookRequest.objects.create(id=request_id, user=self.opponent, date=datetime.now())
		
		self.assertEqual(FacebookRequest.objects.count(), 1)
		self.assertFalse(self.opponent.coreprofile in self.user.coreprofile.allies.all())
		
		response = self.client.get(reverse('canvas'), {'request_ids': request_id})
		
		self.assertEqual(response.status_code, 200)
		self.assertEqual(FacebookRequest.objects.count(), 0)
		self.assertTrue(self.opponent.coreprofile in self.user.coreprofile.allies.all())
	
	def test_accept_request_loads_when_not_logged_in(self):
		self.client.logout()
		request_ids = '123456,7890'
		
		response = self.client.get(reverse('canvas'), {'request_ids': request_ids})
		
		self.assertEqual(response.status_code, 200)
	
	def test_doesnt_panick_on_post_without_csrf_token(self):
		self.client.enforce_csrf_checks = True
		
		response = self.client.post(reverse('canvas'))
		
		self.assertEqual(response.status_code, 200)

class InventoryTestCase(BaseTestCase):
	def test_has_no_item_subclasses(self):
		self.i1.save()
		self.a1.save()
		self.m1.area=self.a1
		self.m1.save()
		self.i1.give_to_user(self.user)
		self.m1.give_to_user(self.user)
		
		response = self.client.get(reverse('inventory'))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.i1.name, count=1)
		self.assertNotContains(response, self.m1.name)
		

class StoreTestCase(BaseTestCase):
	def test_only_has_purchasable_items(self):
		self.i1.price = 0
		self.i1.save()
		self.i2.credit_price = 1
		self.i2.save()
		self.i3.price = 1
		self.i3.credit_price = 1
		self.i3.save()
		self.i4.save()
		
		response = self.client.get(reverse('store'))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.i1.name, count=1)
		self.assertContains(response, self.i2.name, count=1)
		self.assertContains(response, escape(self.i3.name), count=1)
		self.assertNotContains(response, self.i4.name)
		

class AllianceTestCase(BaseTestCase):
	def test_empty(self):
		response = self.client.get(reverse('alliance'))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "You have no allies.")
		self.assertNotContains(response, self.opponent.username)
	
	def test_non_empty(self):
		self.user.coreprofile.allies.add(self.opponent.coreprofile)
		
		response = self.client.get(reverse('alliance'))
		
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, "You have no allies.")
		self.assertContains(response, self.opponent.username)

class StoreRequestIdsTestCase(BaseTestCase):
	def test_storage_successful(self):
		self.assertEqual(self.user.facebookrequest_set.count(), 0)
		
		request_id = '123456'
		
		response = self.client.post(
			reverse('store_alliance_request_ids'),
			data='["%s"]' % request_id,
			content_type='text/json'
		)
		
		self.assertEqual(response.status_code, 200)
		requests = self.user.facebookrequest_set.all()
		self.assertEqual(len(requests), 1)
		self.assertEqual(requests[0].id, request_id)
		

