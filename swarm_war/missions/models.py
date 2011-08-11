# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import logging
#import ipdb
import math
import random

#Django imports
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.utils import safestring

#App imports
from swarm_war.core.exceptions import MaxItemAmountError
from swarm_war.core.models import Item, UserItem
from swarm_war.core.managers import ItemManager
from managers import AreaManager, UserMissionManager, MissionProfileManager

logger = logging.getLogger(__name__)

# Create your models here.

class Area(models.Model):
	"""
	Used to group together missions.
	"""
	#constants
	
	#properties
	objects = AreaManager()
	
	#fields
	name = models.CharField(
		max_length=50,
		unique=True,
		help_text="Human readable name users will see."
	)
	description = models.TextField(blank=True)
	#TODO: make nullable in case you want a different mechanism for unlocking the next area
	percent_to_progress = models.PositiveSmallIntegerField(
		default=lambda: 75,
		help_text="Percentage of missions you need completed to unlock a new area."
	)
	order = models.PositiveIntegerField(
		default=(lambda: Area.objects.count() + 1),
		help_text="The order you want this area to appear in."
	)
	
	#methods
	#TODO: fix. quantity is ignored, but it's left in so the method signature is compatible
	def give_to_user(self, user, quantity=1):
		profile = user.missionprofile
		profile.last_area_viewed = self
		profile.save()
		
		usermissions = []
		
		for mission in self.mission_set.all():
			logger.debug(mission)
			if not mission.secret:
				logger.debug('not secret')
				usermissions.append(mission.give_to_user(user))
		return usermissions
	
	def grant_new(self, user):
		#TODO: only do this if user doesn't have next area
		#don't count secret missions
		total_missions = self.mission_set.filter(secret=False).count()
		#only count 100% missions
		completed_missions = UserMission.objects.filter(progress__gte=Mission.MAX_PROGRESS_PER_TIER, item__mission__secret=False, item__mission__area=self).count()
		
		if (completed_missions/total_missions * 100) >= self.percent_to_progress:
			try:
				logger.debug('granting new area')
				return Area.objects.filter(order__gt=self.order)[0].give_to_user(user)
			except:
				return None
	
	
	_tier_for_user = {}
	def get_tier_for_user(self, user):
		if user.id in self._tier_for_user:
			return self._tier_for_user[user.id]
		
		tier = Mission.NUM_TIERS
		
		ums = UserMission.objects.filter(item__mission__area=self, user=user)
		
		if len(ums) > 0:
			for um in ums:
				m_tier = 1 + (um.progress / Mission.MAX_PROGRESS_PER_TIER)
				if m_tier > Mission.NUM_TIERS:
					m_tier = Mission.NUM_TIERS
				#if the mission's tier is lower than the currently recorded one, that's the new area tier
				if m_tier < tier:
					tier = m_tier
				#1 is the lowest tier possible here, so there's no point in checking the rest
				if tier == 1:
					break
		else:
			#in case no missions for this area have been unlocked, the tier will be 0
			tier = 0
		
		self._tier_for_user[user.id] = tier
		return tier
	
	def natural_key(self):
		return self.name
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ['order', 'id']

class Mission(Item):
	"""
	Stores constants for missions.
	"""
	#constants
	#max progress you can reach is 100%. If we implement multiple levels, we could just increase this value, e.g. 300 for 3 levels, 0-99 is level 1, 100-199 is level 2, 200-299 is level 3
	NUM_TIERS = 3
	MAX_PROGRESS_PER_TIER = 100
	
	#properties
	objects = ItemManager()
	
	show_in_inventory = False
	
	readonly_fields = ['NUM_TIERS', 'MAX_PROGRESS_PER_TIER']
	
	#fields
	area = models.ForeignKey(Area, default=lambda: Area.objects.get_last_or_none())
	progress_step = models.PositiveSmallIntegerField(
		default=lambda: 20,
		help_text="Progress made every time a user performs a mission.")
	#attribute modifiers
	#TODO: make the semantics more consistent for these 4 fields
	base_energy = models.IntegerField(
		default=lambda: -5,
		help_text="Energy gained or lost every time a user performs a mission.")
	base_health = models.IntegerField(
		default=lambda: -5,
		help_text="Health gained or lost every time a user performs a mission.")
	base_experience = models.IntegerField(
		default=lambda: 5,
		help_text="Experience gained or lost every time a user performs a mission.")
	base_money = models.IntegerField(
		default=lambda: 5,
		help_text="Money gained or lost every time a user performs a mission.")
	percent_to_progress = models.PositiveSmallIntegerField(
		default=lambda: 75,
		help_text="Percentage of this mission to complete before unlocking the next mission in the same area."
	)
	
	secret = models.BooleanField(
		default=False,
		help_text="Is this a secret mission? If so, it will not be automatically granted to users when unlocking an area.")
	
	#TODO: restrict quantity to 1
	
	#methods
	@classmethod
	def get_m2m_class(cls):
		return UserMission
	
	#def get_user_m2m(self, user):
	#	try:
	#		return UserMission.objects.get(item=self, user=user)
	#	except UserMission.DoesNotExist:
	#		return UserMission(item=self, user=user, quantity=0)
	
	def give_to_user(self, user, quantity=1, freebie=False):
		ui = super(Mission, self).give_to_user(user, quantity=quantity, freebie=freebie)
		if self.percent_to_progress == 0:
			ms = Mission.objects.filter(area=self.area, order__gt=self.order)
			if len(ms) > 0:
				try:
					ms[0].give_to_user(self.user)
				except:
					pass
		return ui
	
	def natural_key(self):
		return super(Mission, self).natural_key()
	natural_key.dependencies = ['core.item']
	
	#__unicode__() is inherited
	
	class Meta:
		order_with_respect_to = 'area'

class UserMission(UserItem):
	"""
	Stores a user's mission progress.
	If a mission isn't available to a user a UserMission/UserItem instance shouldn't be created yet. When a mission becomes available, a UserMission instance is created with a percentage of 0.
	"""
	#constants
	
	#fields
	progress = models.PositiveSmallIntegerField(default=0)
	old_progress = models.PositiveSmallIntegerField(default=0)
	times_succeeded = models.PositiveIntegerField(default=0)
	
	#properties
	def _get_percent_progress(self):
		return self.progress - (self.item.mission.MAX_PROGRESS_PER_TIER * (self.tier-1))
	percent_progress = property(_get_percent_progress)
	
	def _get_energy(self):
		return self._modify_value(self.item.mission.base_energy)
	energy = property(_get_energy)
	
	def _get_health(self):
		return self._modify_value(self.item.mission.base_health)
	health = property(_get_health)
	
	def _get_experience(self):
		return self._modify_value(self.item.mission.base_experience)
	experience = property(_get_experience)
	
	def _get_money(self):
		return self._modify_value(self.item.mission.base_money)
	money = property(_get_money)
	
	def _modify_value(self, value):
		amount_per_tier = 0.1
		tier = self.tier
		modifier = (tier - 1) * amount_per_tier
		
		if modifier > 0:
			#values greater than 0 are decreased in magnitude
			#negative values are increased in magnitude
			if value > 0:
				value *= 1 - modifier
			elif value < 0:
				value *= 1 + modifier
		
		return long(math.ceil(value))
	
	def _get_tier(self):
		return self.item.mission.area.get_tier_for_user(self.user)
	tier = property(_get_tier)
	
	objects = UserMissionManager()
	
	#methods
	def do_mission(self):
		profile = self.user.coreprofile
		mission = self.item.mission
		
		profile.energy += self.energy
		profile.health += self.health
		profile.experience += self.experience
		profile.money += self.money
		
		if profile.energy < 0:
			raise Exception('You don\'t have enough energy.')
		if profile.health < 0:
			raise Exception('You don\'t have enough health.')
		if profile.experience < 0:
			raise Exception('You don\'t have enough experience.')
		if profile.money < 0:
			raise Exception('You don\'t have enough money.')
		
		items_received = []
		
		#all MissionItems for this Mission
		mis = [mi for mi in MissionItem.objects.all() if mi.mission==mission]
		#all UserItems for Items that are required for this Mission, and where the required quantity is less than or equal to what the user has
		uis = UserItem.objects.filter(
			item__missionitem_requirement__mission=mission, 
			item__missionitem_requirement__quantity__lte=F('quantity')
		)
		has_items = True
		#If there's more MissionItems than there are UserItems of a sufficient quantity
		if len(mis) > len(uis):
			has_items = False
		
		if not has_items:
			raise Exception('you don\'t have the necessary items')
		#logger.debug('User has all items necessary.')
		
		max_progress = mission.area.get_tier_for_user(self.user) * Mission.MAX_PROGRESS_PER_TIER
		self.old_progress = self.progress
		self.progress += mission.progress_step
		self.times_succeeded += 1
		if self.progress > max_progress:
			self.progress = max_progress
		if self.progress >= max_progress and self.progress > self.old_progress:
			#tier for this mission was completed
			profile.attribute_points += 1
		#try to give next mission if possible
		if self.progress >= mission.percent_to_progress:
			ms = Mission.objects.filter(area=mission.area, order__gt=mission.order)
			if len(ms) > 0:
				try:
					ms[0].give_to_user(self.user)
				except:
					pass
		
		#use up consumable items
		for mi in mis:
			if mi.consumable:
				ui = [ui for ui in uis if ui.item == mi.item][0]
				ui.quantity = F('quantity') - mi.quantity
				ui.save()
		try:
			items_received = self.run_triggers()
		except Exception as e:
			logger.debug(e)
		#save last in case any errors are generated, so we won't remove energy without adding progress, or vice versa
		profile.save()
		self.save()
		
		#only call if progress is at least 100%
		if self.progress >= Mission.MAX_PROGRESS_PER_TIER and self.old_progress < Mission.MAX_PROGRESS_PER_TIER:
			mission.area.grant_new(self.user)
		
		return items_received
	
	def run_triggers(self):
		#TODO: fetch all MissionTrigger instances for this UserMission where the threshold is greater than the previous percentage (to prevent retriggering) and less than or equal to the current percentage. But maybe it won't be necessary with query caching.
		triggers = self.item.mission.triggers.all()
		items_received = []
		logger.debug('progress: %s' % self.progress)
		for t in triggers:
			t = t.as_leaf_class()
			#only execute once
			ret = t.run(self)
			if ret is not None:
				if type(ret) is list:
					items_received.extend(ret)
				else:
					items_received.append(ret)
			
		return items_received
	
	def natural_key(self):
		return super(UserMission, self).natural_key()
	natural_key.dependencies = ['core.useritem']
	
	def __unicode__(self):
		return u'%s: Mission=%s, User=%s' % (self.__class__.__name__, unicode(self.item.mission), unicode(self.user))

class MissionItem(models.Model):
	"Items required to do a mission."
	#constants
	
	#properties
	
	#fields
	mission = models.ForeignKey(Mission)
	item = models.ForeignKey(Item, related_name="missionitem_requirement")
	quantity = models.PositiveIntegerField(
		default=1,
		validators=[MinValueValidator(1)],
		help_text="Quantity of this item required to do this mission.")
	consumable = models.BooleanField(
		default=False,
		help_text="If checked, the specified quantity of this item will be deducted from a user's inventory when performing this mission.")
	
	#methods
	def __unicode__(self):
		return u'%s: Mission=%s, Item=%s' % (self.__class__.__name__, unicode(self.mission), unicode(self.item))
	

class MissionTrigger(models.Model):
	"""
	Stores info about what items will be given when.
	When the percentage complete of a mission is between the lower and upper limit (if there is one), the probability will be used to determine if the item should be acquired. When acquired, new relations will be stored in the database between those items and the user to signify permanent ownership. It'll be better than constantly querying MissionTriggers and testing if the conditions apply. Plus items may be acquired through other means such as buying or winning in a battle, and there needs to be a uniform way of expressing ownership for every acquisition method.
	"""
	#constants
	PROBABILITY_MIN = 1
	PROBABILITY_MAX = 100
	
	#properties
	
	#fields
	mission = models.ForeignKey(
		Mission,
		related_name="triggers")
	lower_limit = models.PositiveSmallIntegerField(
		default=0,
		help_text="Lower limit needed to activate this trigger, inclusive.")
	upper_limit = models.PositiveSmallIntegerField(
		null=True,
		blank=True,
		help_text="Upper limit where this trigger can still be activated, inclusive.")
	new_progress_only = models.BooleanField(
		default=lambda: True,
		help_text="Only run trigger when progress is made.")
	probability = models.PositiveSmallIntegerField(
		default=100,
		validators=[MinValueValidator(PROBABILITY_MIN), MaxValueValidator(PROBABILITY_MAX)],
		help_text="Percent probability of acquiring this item when doing a mission.")
	content_type = models.ForeignKey(
		ContentType,
		editable=False,
		blank=True,
		null=True
	)
	#Uses ForeignKey instead of ManyToMany. ManyToMany probably won't get used that often, and it'll make iterating more difficult.
	item = models.ForeignKey(
		Item,
		null=True,
		blank=True,
		help_text="Item a user acquires when limits are met.")
	quantity = models.IntegerField(
		default=1,
		help_text="Quantity that should be given when triggered. Can be a negative number to signify that something is being taken away.")
	
	def as_leaf_class(self):
		model = self.content_type.model_class()
		if(model == MissionTrigger):
			return self
		return model.objects.get(id=self.id)
	
	def run(self, usermission):
		if self.new_progress_only and usermission.progress == usermission.old_progress:
			return
		if usermission.progress >= self.lower_limit:
			if not self.upper_limit or usermission.progress <= self.upper_limit:
				if self.probability == 100 or self.probability >= random.randint(self.PROBABILITY_MIN, self.PROBABILITY_MAX):
					try:
						return self.action(usermission)
					except Exception as e:
						pass
	
	def action(self, usermission):
		if self.item is not None:
			try:
				self.item.give_to_user(usermission.user, self.quantity)
				return self.item
			except MaxItemAmountError:
				pass
	
	def html(self):
		if self.item is not None and self.item.image != '':
			s = u'<img title="%s" src="%s" height="108px" alt="%s" />'
			return safestring.mark_safe(s % (self.item.name, self.item.image.url, self.item.image_alt))
		else:
			return safestring.mark_safe(u'<p>%s</p>' % self.item.name)
	
	#methods
	def __unicode__(self):
		return u'%s: Mission=%s, Item=%s' % (self.__class__.__name__, unicode(self.mission), unicode(self.item))

def missiontrigger_save_handler(sender, instance, **kwargs):
	"Set the content type on save"
	#for all subtypes of Item
	if isinstance(instance, MissionTrigger):
		if instance.content_type is None:
			instance.content_type = ContentType.objects.get_for_model(instance.__class__)
pre_save.connect(missiontrigger_save_handler)

class MissionProfile(models.Model):
	"""
	App level profile. Avoids import error from trying to store app specific data on CoreProfile.
	"""
	#fields
	user = models.OneToOneField(User)
	
	last_area_viewed = models.ForeignKey(
		Area,
		null=True,
		blank=True)
	
	objects = MissionProfileManager()
	
	#methods
	def natural_key(self):
		return (self.user.username)#user has no natural_key() defined :(
	natural_key.dependencies = ['auth.user']
	
	def __unicode__(self):
		return u'%s: %s' % (self.__class__.__name__, self.user)

def create_profile(user):
	"""
	Called using a post_save trigger on User, so when a new User is added a Profile is created as well.
	"""
	#create a profile
	profile = MissionProfile(user=user)
	profile.save()

def user_save_handler(sender, instance, created, **kwargs):
	if created:
		create_profile(instance)
post_save.connect(user_save_handler, sender=User)

