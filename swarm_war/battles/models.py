# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

# Create your models here.

class BattleRecord(models.Model):
	attacker = models.ForeignKey(User, related_name="battlerecord_attacker_set")
	attacker_health_lost = models.PositiveIntegerField(null=True)
	attacker_money_lost = models.PositiveIntegerField(null=True)
	attacker_experience_gained = models.PositiveIntegerField(null=True)
	attacker_killed = models.NullBooleanField()
	defender = models.ForeignKey(User, related_name="battlerecord_defender_set")
	defender_health_lost = models.PositiveIntegerField(null=True)
	defender_money_lost = models.PositiveIntegerField(null=True)
	defender_experience_gained = models.PositiveIntegerField(null=True)
	defender_killed = models.NullBooleanField()
	
	attacker_won = models.NullBooleanField()
	datetime = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return u'%s attacked %s dealing %s damage and receiving %s damage. %s lost %s money and gained %s XP, %s lost %s money and gained %s XP.' % (
			self.attacker.first_name,
			self.defender.first_name,
			self.defender_health_lost,
			self.attacker_health_lost,
			self.attacker.first_name,
			self.attacker_money_lost,
			self.attacker_experience_gained,
			self.defender.first_name,
			self.defender_money_lost,
			self.defender_experience_gained,
		)
	
	class Meta:
		ordering = ['datetime']

class BattleProfile(models.Model):
	user = models.OneToOneField(User)
	attacked_and_won = models.PositiveIntegerField(default=0)
	attacked_and_lost = models.PositiveIntegerField(default=0)
	defended_and_won = models.PositiveIntegerField(default=0)
	defended_and_lost = models.PositiveIntegerField(default=0)
	killed = models.PositiveIntegerField(default=0)
	kills = models.PositiveIntegerField(default=0)

def create_profile(user):
	"""
	Called using a post_save trigger on User, so when a new User is added a Profile is created as well.
	"""
	#create a profile
	profile = BattleProfile(user=user)
	profile.save()

def user_save_handler(sender, instance, created, **kwargs):
	if created:
		create_profile(instance)
post_save.connect(user_save_handler, sender=User)
