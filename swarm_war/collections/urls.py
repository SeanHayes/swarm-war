# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.conf.urls.defaults import *

# place app url patterns here
urlpatterns = patterns('swarm_war.collections.views',
	url(r'^$', 'collections', name="collections"),
	url(r'^(.+)/redeem/$', 'redeem_collection', name="redeem_collection"),
)
