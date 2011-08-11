# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.conf.urls.defaults import *

# place app url patterns here
urlpatterns = patterns('swarm_war.battles.views',
	url(r'^$', 'index', name="battles_index"),
	url(r'^(\d+)/attack/$', 'attack_user', name="attack_user"),
)
