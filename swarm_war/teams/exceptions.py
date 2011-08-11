# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import logging

logger = logging.getLogger(__name__)

# place exception definitions here

class Error(Exception):
	"""Base class for exceptions in this module."""
	def __str__(self):
		return self.msg

class TeamAlreadyExistsError(Error):
	msg = 'A team with that name already exists.'

class TeamNoLongerExistsError(Error):
	msg = 'Team doesn\'t exist anymore.'

class TeamFullError(Error):
	msg = 'Team is full.'

class NotOnATeamError(Error):
	msg = '%s is not on a team.'
	user = None
	
	def __init__(self, *args, **kwargs):
		if len(args) > 0:
			self.user = args[0]
		super(NotOnATeamError, self).__init__(*args, **kwargs)
	
	def __str__(self):
		return self.msg % self.user if self.user is not None else 'User'

class TeamAlreadyHasALeaderError(Error):
	msg = 'Team already has a leader.'

class NotALeaderError(Error):
	msg = 'You are not a leader of this team.'

class NotOnSameTeamError(Error):
	msg = 'You are not on the same team.'
