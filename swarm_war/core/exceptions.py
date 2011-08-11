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

class MaxItemAmountError(Error):
	msg = 'You already have the max amount of this item.'

