# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import logging
import pdb

#Django imports
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.db.models.signals import post_save
from django.utils import safestring

#App imports
from exceptions import TeamAlreadyExistsError, TeamNoLongerExistsError, TeamFullError, NotOnATeamError, TeamAlreadyHasALeaderError, NotOnSameTeamError, NotALeaderError
from managers import *
from swarm_war.core.models import FacebookRequest
from swarm_war.core.managers import FacebookRequestManager

logger = logging.getLogger(__name__)

# Create your models here.

MAX_TEAM_SIZE = 10

class Team(models.Model):
	name = models.CharField(unique=True, max_length=100)
	
	def get_leader(self):
		leader = None
		try:
			#TODO: use filter to better tolerate bugs (e.g. more than one leader) that may creep up
			leader = self.members.get(leader=True).user
		except TeamProfile.DoesNotExist:
			pass
		except Exception as e:
			logger.error(e)
		
		return leader
	
	def html(self):
		s = u'<a href="%s">%s</a>' % (reverse('teams_view', args=[self.id]), self.name)
		return safestring.mark_safe(s)
	
	def __unicode__(self):
		return self.name

class TeamProfile(models.Model):
	user = models.OneToOneField(User)
	team = models.ForeignKey(Team, null=True, blank=True, related_name="members")
	leader = models.BooleanField(default=False)
	#TODO: need a leave_team() method that cleans up teams with no members left
	def become_leader(self):
		if self.team is None:
			raise NotOnATeamError(self.user)
		elif self.team.get_leader() is not None:
			raise TeamAlreadyHasALeaderError()
		else:
			self.leader = True
			self.save()
	
	def create_team(self, name):
		try:
			team = Team(name=name)
			team.save()
		except IntegrityError as e:
			raise TeamAlreadyExistsError()
		self.team = team
		self.leader = True
		self.save()
		return team
	
	def join_team(self, team):
		count = team.members.count()
		
		if count < MAX_TEAM_SIZE:
			self.team = team
			self.leader = False
			self.save()
		else:
			raise TeamFullError()
	
	def kick_out(self, user):
		if self.team is None:
			raise NotOnATeamError(self.user)
		if not self.leader:
			raise NotALeaderError()
		
		user_tp = TeamProfile.objects.get(user=user)
		
		if user_tp.team is None:
			raise NotOnATeamError(user)
		if user_tp.team.id is not self.team.id:
			raise NotOnSameTeamError()
		
		user_tp.leave_team()
	
	def leave_team(self):
		team = self.team
		
		self.team = None
		self.leader = False
		self.save()
		
		count = team.members.count()
		if count == 0:
			team.delete()
	
	def __unicode__(self):
		return u'%s: %s' % (self.__class__.__name__, self.user)

def create_profile(user):
	"""
	Called using a post_save trigger on User, so when a new User is added a Profile is created as well.
	"""
	#create a profile
	profile = TeamProfile(user=user)
	profile.save()

def user_save_handler(sender, instance, created, **kwargs):
	if created:
		create_profile(instance)
post_save.connect(user_save_handler, sender=User)

class TeamFacebookRequest(FacebookRequest):
	#has to be nullable so that this doesn't get deleted when a related team gets deleted
	team = models.ForeignKey(Team, null=True)
	
	objects = FacebookRequestManager()
	
	def html(self):
		s = u'%s has invited you to join a Team: %s.' % (self.user.username, self.team.html)
		return safestring.mark_safe(s)
	
	def confirm(self, friend):
		try:
			if self.team is None:
				raise TeamNoLongerExistsError()
			if self.user.id not in [u.id for u in self.team.members.all()]:
				raise Exception('Can\'t join %s because %s isn\'t a member anymore.' % (self.team.name, self.user.username))
			
			friend.teamprofile.join_team(self.team)
		finally:
			super(TeamFacebookRequest, self).confirm(friend)

