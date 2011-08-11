# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import math
import facebook
#import ipdb
import logging
import string
import traceback

#Django imports
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save, pre_save, post_delete
from django.utils import safestring

#App imports
from exceptions import MaxItemAmountError
from managers import ItemManager, UserItemManager, CoreProfileManager, FacebookRequestManager

logger = logging.getLogger(__name__)

# Create your models here.

class ItemCategory(models.Model):
	name = models.CharField(
		max_length=50,
		unique=True,
		help_text="Human readable name users will see.")

class Item(models.Model):
	"""
	Base class for all aquirable items.
	"""
	#constants
	
	#properties
	objects = ItemManager()
	
	show_in_inventory = True
	show_in_store = True
	
	#fields
	name = models.CharField(
		max_length=50,
		unique=True,
		help_text="Human readable name users will see."
	)
	description = models.TextField(blank=True)
	category = models.ForeignKey(ItemCategory, null=True, blank=True)
	
	order = models.PositiveIntegerField(
		default=(lambda: Item.objects.count() + 1),
		#unique=True,#TODO: make unique when you have inline admin for ordering
		help_text="The order you want this item to appear in. Useful if you want this item to appear in between existing items in a list."
	)
	
	#allow null to signify no limit
	max_quantity = models.PositiveIntegerField(
		default=1,
		validators=[MinValueValidator(1)],
		null=True,
		blank=True,
		help_text="Maximum number of this item a user can have. Leave blank for items which have no limit."
	)
	
	#null means it's not purchasable and will have to be acquired through missions, battles, etc.
	#any item with a price of 0 or more will appear in the store.
	price = models.PositiveIntegerField(
		null=True,
		blank=True,
		help_text="Leave blank for items that can't be purchased and must be won through missions, battles, etc. Enter 0 for items which are free."
	)
	
	def _get_sell_price(self):
		return self.price / 2
	sell_price = property(_get_sell_price)
	
	credit_price = models.PositiveIntegerField(
		default=0,
		help_text="Only used for items that can be bought with credits."
	)
	
	#TODO: have a smaller version be automatically generated on save (using ExactImage)
	#TODO: should also convert image to PNG
	#TODO: store images using IDs, not original file name, if possible
	image = models.ImageField(
		null=True,
		blank=True,
		upload_to='items/images/%Y/%m',
		help_text="Full sized image of this item."
	)
	#TODO: if not provided, use name
	image_alt = models.TextField(
		null=True,
		blank=True,
		help_text="Text displayed while image is loading, if image is unavailable, or if application is accessed through a screen reader. Should be a description of the image content."
	)
	#TODO: remove this stuff, it's deprecated
	def _get_image_preview(self):
		return self.image
	image_preview = property(_get_image_preview)
	def _get_image_preview_alt(self):
		return self.image_alt
	image_preview_alt = property(_get_image_preview_alt)
	attack = models.IntegerField(
		default=0
	)
	defense = models.IntegerField(
		default=0
	)
	#TODO: add other attribute modifiers
	#TODO: add creation date
	
	#any way to put this on User model? It would make more sense (User.items).
	#Could put it on CoreProfile, but User is used for everything else
	users = models.ManyToManyField(User, through="UserItem")
	
	content_type = models.ForeignKey(
		ContentType,
		editable=False,
		blank=True,
		null=True
	)
	
	#methods
	def get_attribute_field_names(self):
		return ['attack', 'defense']
	
	def get_attributes_display_list(self):
		field_names = self.get_attribute_field_names()
		l = []
		for field_name in field_names:
			value = self.__getattribute__(field_name)
			if value is not None:
				field = self._meta.get_field(field_name)
				name = string.capwords(field.verbose_name)
				help_text = field.help_text
				l.append((name, value, help_text,))
		return l
	
	def as_leaf_class(self):
		model = self.content_type.model_class()
		if(model == Item):
			return self
		return model.objects.get(id=self.id)
	
	@classmethod
	def get_m2m_class(cls):
		return UserItem
	
	def get_user_m2m(self, user):
		"Returns a UserItem object that represents a ManyToMany relation between Item and User. Subtypes of Item can override this method and return a subclass of of UserItem if additional info needs to be stored for that relation."
		m2m_class = self.__class__.get_m2m_class()
		try:
			return m2m_class.objects.get(item=self, user=user)
		except m2m_class.DoesNotExist:
			return m2m_class(item=self, user=user, quantity=0)
	
	def give_to_user(self, user, quantity=1, freebie=False):
		ui = self.as_leaf_class().get_user_m2m(user)
		orig_quantity = ui.quantity
		#logger.debug('orig_quantity: %s' % orig_quantity)
		ui.quantity += quantity
		#logger.debug('ui.quantity: %s' % ui.quantity)
		
		#logger.debug('Had %s, max is %s.' % (orig_quantity, self.max_quantity))
		if self.max_quantity:
			if orig_quantity >= self.max_quantity:
				raise MaxItemAmountError()
			
			if ui.quantity > self.max_quantity:
				ui.quantity = self.max_quantity
		
		if not freebie and ((self.price is not None and self.price > 0) or self.credit_price > 0):
			profile = user.coreprofile
			quantity_delta = ui.quantity - orig_quantity
			price = self.price * quantity_delta if self.price is not None else 0
			credit_price = self.credit_price * quantity_delta
			profile.auto_charge(price, credits=credit_price)
		ui.save()
		return ui
	
	def natural_key(self):
		return (self.name)
	natural_key.dependencies = ['contenttypes.contenttype']
	
	def __unicode__(self):
		return u'%s: %s' % (self.content_type.model_class().__name__, self.name)
	
	class Meta:
		ordering = ['order', 'id']

def item_save_handler(sender, instance, **kwargs):
	"Set the content type on save"
	#for all subtypes of Item
	if isinstance(instance, Item):
		if instance.content_type is None:
			instance.content_type = ContentType.objects.get_for_model(instance.__class__)
pre_save.connect(item_save_handler)

class UserItem(models.Model):
	"""
	Joins Item and User to signify ownership.
	"""
	#constants
	
	#properties
	objects = UserItemManager()
	
	#fields
	item = models.ForeignKey(Item)
	user = models.ForeignKey(User)
	#TODO: add last saved timestamp
	#TODO: add contenttype for subclasses
	
	quantity = models.PositiveIntegerField(
		default=1,
		validators=[MinValueValidator(0)],
		help_text="Number of this item a user currently has.")
	
	#methods
	def __unicode__(self):
		return u'%s: Item=%s, User=%s' % (self.__class__.__name__, unicode(self.item), unicode(self.user))
	
	def natural_key(self):
		return (self.item, self.user)
	natural_key.dependencies = ['core.item', 'auth.user']
	
	def sell(self, quantity):
		if self.item.credit_price > 0:
			raise Exception('This item can\'t be sold because credit transactions aren\'t reversible.')
		if quantity > self.quantity:
			raise Exception('You don\'t have that many of this item.')
		if self.item.price is None:
			raise Exception('This item has no price and can\'t be sold.')
		
		self.quantity -= quantity
		self.save()
		
		prof = self.user.coreprofile
		prof.money += quantity * self.item.sell_price
		prof.save()
	
	class Meta:
		unique_together = ("item", "user")
		#order_with_respect_to = 'item'

class FacebookRequest(models.Model):
	"""
	Stores data about a request. Used to keep track of what requests haven't been accepted so they can be deleted after a long period of time.
	More Info: http://developers.facebook.com/docs/reference/dialogs/requests/
	"""
	#fb_id is a char field since it's always possible Facebook will use non-numerical characters in the future (some of their UIDs are already usernames)
	id = models.CharField(max_length=20, primary_key=True)
	user = models.ForeignKey(User)
	date = models.DateTimeField()
	content_type = models.ForeignKey(
		ContentType,
		editable=False,
		blank=True,
		null=True)
	
	objects = FacebookRequestManager()
	
	def html(self):
		s = u'%s has invited you to his/her Alliance.' % self.user.username
		return safestring.mark_safe(s)
	
	def as_leaf_class(self):
		model = self.content_type.model_class()
		if(model == FacebookRequest):
			return self
		return model.objects.get(id=self.id)
	
	def confirm(self, friend):
		self.user.coreprofile.add_ally(friend.coreprofile)
		try:
			graph = facebook.GraphAPI(friend.facebook.access_token)
			#there's bugs in the FB SDK and API that causes this to randomly throw an error
			graph.delete_object(self.id)
		except Exception as e:
			logger.debug(e)
		finally:
			self.delete()
	
	def decline(self):
		try:
			graph = facebook.GraphAPI(self.user.facebook.access_token)
			#there's bugs in the FB SDK and API that causes this to randomly throw an error
			graph.delete_object(self.id)
		except Exception as e:
			logger.debug(e)
		finally:
			self.delete()
	
	def __unicode__(self):
		return u'%s sent request #%s on %s' % (self.user, self.id, self.date)
	
	class Meta:
		ordering = ['date']

def facebookrequest_pre_save_handler(sender, instance, **kwargs):
	if isinstance(instance, FacebookRequest):
		if instance.content_type is None:
			instance.content_type = ContentType.objects.get_for_model(instance.__class__)
pre_save.connect(facebookrequest_pre_save_handler)

class CoreProfile(models.Model):
	"""The game's profile model."""
	#constants
	MAX_ALLIANCE_SIZE = 750
	REFILL_DATA = {
		#attribute: num_tokens required to refill
		'energy': 10,
		'stamina': 10,
		'health': 10,
	}
	
	#properties
	objects = CoreProfileManager()
	#whether or not the presave handler should reduce stats to maximum
	cap_attributes = True
	
	#fields
	user = models.OneToOneField(User)
	
	#player attributes
	#defaults are lambdas to prevent enforcement at DB level so they can be easily changed without the need for migrations
	#TODO: add properties that compute attribute values
	attack = models.PositiveIntegerField(default=lambda: 1)
	defense = models.PositiveIntegerField(default=lambda: 1)
	max_health = models.PositiveIntegerField(default=lambda: 50)
	health = models.PositiveIntegerField(default=max_health.default)
	max_energy = models.PositiveIntegerField(default=lambda: 10)
	energy = models.PositiveIntegerField(default=max_energy.default)
	max_stamina = models.PositiveIntegerField(default=lambda: 10)
	stamina = models.PositiveIntegerField(default=max_stamina.default)
	money = models.PositiveIntegerField(default=lambda: 10, help_text="Money that's not in the bank.")
	banked_money = models.PositiveIntegerField(default=lambda: 0, help_text="Money that's in the bank and safe from theft.")
	def _get_total_money(self):
		return self.money + self.banked_money
	total_money = property(_get_total_money)
	credits = models.PositiveIntegerField(default=lambda: 0, help_text="Credits are virtual currency.")
	
	attribute_field_names = ['attack', 'defense', 'max_health', 'max_energy', 'max_stamina', 'alliance_size']
	def get_attribute_fields(self):
		d = {}
		for k in self.attribute_field_names:
			d[k] = self.__getattribute__(k)
		return d
	
	attribute_points = models.PositiveIntegerField(default=lambda: 0, help_text="Points that can be used to increase max health, energy, etc.")
	
	experience = models.PositiveIntegerField(default=lambda: 0)
	leveled_up = models.BooleanField(default=False)
	old_level = models.PositiveIntegerField(null=True, blank=True)
	
	allies = models.ManyToManyField('self', blank=True)
	alliance_size = models.PositiveIntegerField(
		default=0,
		validators=[MaxValueValidator(MAX_ALLIANCE_SIZE)],
	)
	
	def _get_total_attack_defense(self):
		ad = UserItem.objects.get_attack_defense(user=self.user)
		
		#multiplier for having alliance members
		#max multiplier is 50%
		m = self.alliance_size
		if m > 500:
			m = 500
		m = 1 + long(m) / 1000
		
		return {
			'attack': m * (self.attack + ad['item__attack__sum']),
			'defense': m * (self.defense + ad['item__defense__sum']),
		}
	total_attack_defense = property(_get_total_attack_defense)
	
	#methods
	def get_experience_level(self):
		if settings.DW_CORE_XP_LEVEL_MATH_FUNC:
			return settings.DW_CORE_XP_LEVEL_MATH_FUNC(self)
		
		xp = self.experience
		level = 0
		
		for levels, increment in settings.DW_CORE_XP_LEVEL_ITERATOR():
			tmp_level = levels
			
			for i in xrange(levels, 0, -1):
				if (i * increment) > xp:
					tmp_level = i
				else:
					break
			level += tmp_level
			xp -= levels * increment
			if xp <= 0:
				break
		
		return level
	
	def level_up(self):
		self.leveled_up = True
		new_xp_level = self.get_experience_level()
		levels_increased = new_xp_level - self.old_level
		
		self.attribute_points = F('attribute_points') + (5 * levels_increased)
		self.old_level = new_xp_level
		
		if self.health < self.max_health:
			self.health = self.max_health
		if self.stamina < self.max_stamina:
			self.stamina = self.max_stamina
		if self.energy < self.max_energy:
			self.energy = self.max_energy
	
	def deposit(self, money, save=True):
		"Moves money from a user's available cash to the bank, deducting a 10% fee."
		if type(money) is not int and type(money) is not long:
			raise Exception('Your deposit amount must be an integer.')
		if money <= 0:
			raise Exception('Your deposit amount must be greater than 0.')
		if money > self.money:
			raise Exception('You don\'t have enough money.')
		self.money = F('money') - money
		self.banked_money = F('banked_money') + int(math.floor(money * 0.9))
		if save:
			self.save()
	
	def withdraw(self, money, save=True):
		"Moves money from bank to user's available money."
		if type(money) is not int or type(money) is not long:
			raise Exception('Your withdrawal amount must be an integer.')
		if money <= 0:
			raise Exception('Your withdrawal amount must be greater than 0.')
		elif money > self.banked_money:
			raise Exception('You don\'t have enough money in the bank.')
		
		self.banked_money = F('banked_money') - money
		self.money = F('money') + money
		if save:
			self.save()
	
	def auto_charge(self, money, credits=0, save=True):
		"Charges a user money and credits, withdrawing money from CoreProfile.money first and CoreProfile.banked_money second."
		if type(money) is not int and type(money) is not long:
			raise Exception('Amount of money to charge must be an integer.')
		if type(credits) is not int and type(credits) is not long:
			raise Exception('Amount of credits to charge must be an integer.')
		if credits < 0:
			raise Exception('Amount of credits to charge must be 0 or greater.')
		if money < 0:
			raise Exception('Amount of money to charge must be 0 or greater.')
		if money > self.total_money:
			raise Exception('You don\'t have enough money.')
		if credits > self.credits:
			raise Exception('You don\'t have enough credits.')
		
		self.credits -= credits
		self.money -= money
		if self.money < 0:
			self.banked_money += self.money
			self.money = 0
		if save:
			self.save()
	
	def skill_up(self, attr, num, save=True):
		"Increases an attribute using attribute points."
		if type(attr) is not str and type(attr) is not unicode:
			raise Exception('Attribute must be a string.')
		if attr not in self.attribute_field_names:
			raise Exception('There is no attribute "%s".' % attr)
		if type(num) is not int and type(num) is not long:
			raise Exception('Num must be an integer.')
		if num <= 0:
			raise Exception('Num must be greater than 0.')
		if num > self.attribute_points:
			raise Exception('You don\'t have enough attribute points.')
		
		self.attribute_points -= num
		self.__setattr__(attr, self.__getattribute__(attr)+num)
		if save:
			self.save()
	
	def cost_to_heal(self):
		return (self.max_health - self.health) * 100
	
	def add_ally(self, user_profile):
		self.alliance_size += 1
		if user_profile is not None:
			self.allies.add(user_profile)
		self.save()
	
	def refill(self, attr, save=True):
		if attr not in self.REFILL_DATA:
			raise Exception('Can not refill %s' % attr)
		self.auto_charge(0, credits=self.REFILL_DATA[attr], save=False)
		self.__setattr__(attr, self.__getattribute__('max_'+attr))
		if save:
			self.save()
	
	#causes error during fixture dump for some reason
	#def natural_key(self):
	#	return (self.user.username)#user has no natural_key() defined :(
	#natural_key.dependencies = ['auth.user']
	
	def __unicode__(self):
		return u'%s: %s' % (self.__class__.__name__, self.user)

def create_profile(user):
	"""
	Called using a post_save trigger on User, so when a new User is added a Profile is created as well.
	"""
	#create a profile
	profile = CoreProfile(user=user)
	profile.save()

def user_post_save_handler(sender, instance, created, **kwargs):
	if created:
		create_profile(instance)
post_save.connect(user_post_save_handler, sender=User)

def coreprofile_pre_save_handler(sender, instance, **kwargs):
	if instance.id is None:
		instance.old_level = instance.get_experience_level()
	else:
		el = instance.old_level
		el2 = instance.get_experience_level()
		
		if el is not None and el < el2:
			instance.level_up()
	
	if instance.health < 0:
		instance.health = 0
	if instance.cap_attributes:
		if instance.health > instance.max_health:
			instance.health = instance.max_health
		if instance.stamina > instance.max_stamina:
			instance.stamina = instance.max_stamina
		if instance.energy > instance.max_energy:
			instance.energy = instance.max_energy
	if instance.alliance_size > instance.MAX_ALLIANCE_SIZE:
		instance.alliance_size = instance.MAX_ALLIANCE_SIZE
pre_save.connect(coreprofile_pre_save_handler, dispatch_uid="coreprofile_pre_save_handler", sender=CoreProfile)

