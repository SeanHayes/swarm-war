# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Listing(models.Model):
	title = models.TextField(
		blank=True,
		max_length=50,
		help_text="Description of this deal.")
	description = models.TextField(
		blank=True,
		max_length=175,
		help_text="Description of this deal.")
	num_game_credits = models.PositiveIntegerField(
		default=10,
		help_text="Number of in game credits that will be purchased.")
	num_fb_credits = models.PositiveIntegerField(
		default=10,
		help_text="Number of Facebook Credits that the in game credits will be purchased for.")
	
	def get_title(self):
		return self.title if len(self.title) > 0 else u'%s Credits' % self.num_game_credits
	
	def get_description(self):
		return self.description if len(self.description) > 0 else u'Buy %s in-game credits for %s Facebook credits.' % (self.num_game_credits, self.num_fb_credits)
	
	def _get_image_url(self):
		return 'http://www.facebook.com/images/gifts/21.png'
	image_url = property(_get_image_url)
	
	def _get_product_url(self):
		return 'http://www.facebook.com/images/gifts/21.png'
	product_url = property(_get_product_url)
	
	def __unicode__(self):
		return self.get_description()
	
	class Meta:
		ordering = ['-num_game_credits', 'num_fb_credits', '-id']

class PurchaseRecord(models.Model):
	receiver = models.ForeignKey(User)
	listings = models.ManyToManyField(Listing)
	datetime = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['datetime']

