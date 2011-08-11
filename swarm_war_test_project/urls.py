# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

from django.conf.urls.defaults import patterns, include, url
from django.http import HttpResponse

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	# Examples:
	# url(r'^$', 'swarm_war_test_project.views.home', name='home'),
	# url(r'^swarm_war_test_project/', include('swarm_war_test_project.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	# url(r'^admin/', include(admin.site.urls)),
	(r'^', include('swarm_war.core.urls')),
	(r'^battles/', include('swarm_war.battles.urls')),
	(r'^collections/', include('swarm_war.collections.urls')),
	(r'^credits/', include('swarm_war.credits.urls')),
	(r'^leaderboard/', include('swarm_war.leaderboard.urls')),
	(r'^missions/', include('swarm_war.missions.urls')),
	(r'^teams/', include('swarm_war.teams.urls')),
	
	url(r'accounts/login/', lambda request: HttpResponse('', status=302)),
)
