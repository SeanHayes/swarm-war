# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import logging

#Django imports
from django import forms

#App imports
from models import Team

logger = logging.getLogger(__name__)

# place form definitions here
class TeamForm(forms.ModelForm):
	class Meta:
		model = Team

