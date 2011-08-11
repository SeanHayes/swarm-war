# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

from django.conf.urls.defaults import *

# place app url patterns here
urlpatterns = patterns('swarm_war.credits.views',
	url(r'^$', 'index', name="credits_index"),
	url(r'^fb_callback/$', 'fb_callback', name="credits_fb_callback"),
)
