# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.db import models

#App imports
from swarm_war.core.managers import ItemManager

class AreaManager(models.Manager):
	def get_by_natural_key(self, name):
		return self.get(name=name)
	
	def get_last_or_none(self):
		try:
			return self.all().order_by('-order')[0]
		except:
			return None

class UserMissionManager(models.Manager):
	def get_by_natural_key(self, item, user):
		return self.get(item=item, user=user)

class MissionProfileManager(models.Manager):
	"""Custom manager for a Mission Profile."""
	
	def get_by_natural_key(self, username):
		return self.get(user_username=username)

