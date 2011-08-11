# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.conf.urls.defaults import *

# place app url patterns here
urlpatterns = patterns('swarm_war.missions.views',
	url(r'^$', 'index', name="area_index"),
	url(r'^(\d+)/$', 'view', name="area_view"),
	url(r'^missions/(\d+)/execute/$', 'do_mission', name="missions_do_mission"),
)
