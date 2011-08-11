# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.conf.urls.defaults import *

# place app url patterns here
urlpatterns = patterns('swarm_war.teams.views',
	url(r'^$', 'index', name="teams_index"),
	url(r'^my_team/$', 'view_my_team', name="teams_view_my_team"),
	url(r'^create/$', 'create', name="teams_create"),
	url(r'^leave/$', 'leave', name="teams_leave"),
	url(r'^kick_out/(.+)/$', 'kick_out', name="teams_kick_out"),
	url(r'^lead/$', 'become_leader', name="teams_become_leader"),
	url(r'^(.+)/store_request_ids/$', 'store_request_ids', name="teams_store_request_ids"),#AJAX
	url(r'^(.+)/$', 'view', name="teams_view"),
)
