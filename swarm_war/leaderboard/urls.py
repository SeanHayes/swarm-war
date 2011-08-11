# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.conf.urls.defaults import *

# place app url patterns here
urlpatterns = patterns('swarm_war.leaderboard.views',
	url(r'^$', 'index', name="leaderboard_index"),
	url(r'^(.*)/$', 'view', name="leaderboard_view"),
)
