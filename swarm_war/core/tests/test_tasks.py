# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports

#Django imports
from django.conf import settings

#App imports
from ..tasks import energy_tick, stamina_tick, health_tick, facebook_post
from django_facebook_oauth.models import FacebookUser

#Test imports
from util import BaseTestCase

class EnergyTickTestCase(BaseTestCase):
	def test(self):
		energy_tick()

class StaminaTickTestCase(BaseTestCase):
	def test(self):
		stamina_tick()

class HealthTickTestCase(BaseTestCase):
	def test(self):
		health_tick()

class FacebookPostTestCase(BaseTestCase):
	def test_profile_created(self):
		#TODO: mock facebook library
		fb = FacebookUser(user=self.user)
		fb.save()

