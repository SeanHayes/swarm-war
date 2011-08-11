# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import logging
import pdb

#Django imports
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

class ItemManager(models.Manager):
	def get_inventory_item_classes(self):
		qs = ContentType.objects.distinct().filter(item__isnull=False)
		model_classes = [t.model_class() for t in qs if t.model_class().show_in_inventory]
		
		return model_classes
	
	def get_store_item_classes(self):
		qs = ContentType.objects.distinct().filter(item__isnull=False)
		model_classes = [t.model_class() for t in qs if t.model_class().show_in_store]
		
		return model_classes
	
	def get_store_items(self):
		qs = self.filter(content_type=ContentType.objects.get_for_model(self.model))
		
		return qs.filter(Q(price__isnull=False) | Q(credit_price__gt=0))
	
	def get_by_type(self, model_class):
		return self.filter(content_type=ContentType.objects.get_for_model(model_class))
	
	def get_by_natural_key(self, name):
		return self.get(name=name)

class UserItemManager(models.Manager):
	def get_by_type(self, model_class):
		return self.filter(item__content_type=ContentType.objects.get_for_model(model_class))
	
	def get_by_natural_key(self, item, user):
		return self.get(item=item, user=user)
	
	def get_attack_defense(self, user):
		d = self.filter(user=user).aggregate(models.Sum('item__attack'), models.Sum('item__defense'))
		for key in d.keys():
			if d[key] is None:
				d[key] = 0
		return d
	
	def get_inventory_useritems(self, user, t):
		qs = self.filter(item__content_type=ContentType.objects.get_for_model(t))
		
		return qs.filter(user=user)
	
	def get_by_user(self, user):
		return self.filter(user=user)

class ExperienceLevelManager(models.Manager):
	def get_by_experience(self, experience):
		level = None
		for el in self.all():
			if el.threshold <= experience:
				level = el
			else:
				break
		return level

class CoreProfileManager(models.Manager):
	"""Custom manager for a CoreProfile."""
	
	def get_by_natural_key(self, username):
		return self.get(user_username=username)

class FacebookRequestManager(models.Manager):
	def get_by_type(self, model_class):
		return self.filter(content_type=ContentType.objects.get_for_model(model_class))
	
	def create_many(self, ids, *args, **kwargs):
		#pdb.set_trace()
		ret = []
		for i in ids:
			ret.append(self.create(id=i, *args, **kwargs))
		return ret
