# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import pdb
import logging

#Django imports
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F

#App imports
from ..core.models import Item, UserItem

logger = logging.getLogger(__name__)

# Create your models here.

class Collection(models.Model):
	"A group of Items that can be traded in for something else."
	
	#fields
	name = models.CharField(
		max_length=30,
		unique=True,
		help_text="Human readable name users will see.")
	items = models.ManyToManyField(Item, through='CollectionItem')
	prize = models.ForeignKey(Item, related_name='prize_for_collections')
	
	def get_useritems(self, user):
		"Returns UserItem objects matching this Collection."
		return UserItem.objects.filter(user=user, item__collection=self)
	
	def get_sufficient_useritems(self, user):
		"Returns UserItem objects matching this Collection of which a user has sufficient quantity."
		return UserItem.objects.filter(user=user, item__collection=self, item__collectionitem__quantity__lte=F('quantity'))
	
	def has_enough_items(self, user):
		ui_c = self.get_sufficient_useritems(user).count()
		if ui_c == self.collectionitem_set.count():
			return True
		else:
			return False
	
	def redeem(self, user):
		#very expensive, but it probably won't get used that much
		uis = self.get_sufficient_useritems(user)
		cis = self.collectionitem_set.all()
		
		if len(uis) == len(cis):
			for ui in uis:
				for ci in cis:
					if ci.item == ui.item:
						ui.quantity = F('quantity') - ci.quantity
						ui.save()
			
			self.prize.give_to_user(user)
			return self.prize
		else:
			raise Exception('You don\'t have enough items to complete this collection.')
	
	def __unicode__(self):
		return u'%s: %s' % (self.__class__.__name__, unicode(self.name))
	
	def natural_key(self):
		return (self.name)

class CollectionItem(models.Model):
	"ManyToMany table between Collection and Item."
	item = models.ForeignKey(Item)
	collection = models.ForeignKey(Collection)
	quantity = models.PositiveIntegerField(
		default=1,
		validators=[MinValueValidator(1)],
		help_text="Number of this item required to complete the Collection.")
	
	def __unicode__(self):
		return u'%s: Mission=%s, User=%s' % (self.__class__.__name__, unicode(self.item), unicode(self.collection))
	
	def natural_key(self):
		return (self.item, self.collection)
	natural_key.dependencies = ['core.item', 'core.collection']

