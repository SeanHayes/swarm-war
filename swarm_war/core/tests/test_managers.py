# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
from datetime import datetime
import pdb
import urllib

#App imports
from ..models import Item
from util import BaseTestCase

class ItemManagerTestCase(BaseTestCase):
	def test_get_store_items(self):
		self.i1.save()
		self.i2.price = 1
		self.i2.save()
		self.i3.credit_price = 5
		self.i3.save()
		self.i4.price = 0
		self.i4.credit_price = 1
		self.i4.save()
		
		qs = Item.objects.get_store_items()
		
		self.assertTrue(self.i1 not in qs)
		self.assertTrue(self.i2 in qs)
		self.assertTrue(self.i3 in qs)
		self.assertTrue(self.i4 in qs)


