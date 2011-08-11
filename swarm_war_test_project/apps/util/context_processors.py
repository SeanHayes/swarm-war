# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.conf import settings
from django.contrib.sites.models import Site

def current_site(request):
	current_site = None
	try:
		current_site = Site.objects.get_current()
	except Site.DoesNotExist:
		pass
	return {'current_site': current_site}

def settings_in_templates(request):
	keys = getattr(settings, 'SETTINGS_IN_TEMPLATES', [])
	d = {}
	for key in keys:
		d[key] = settings._wrapped.__dict__[key]
	
	return d

