# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.conf.urls.defaults import *

# place app url patterns here
urlpatterns = patterns('swarm_war.core.views',
	url(r'^$', 'canvas', name="canvas"),
	url(r'^inventory/$', 'inventory', name="inventory"),
	url(r'^store/$', 'store', name="store"),
	#TODO: add item view
	url(r'^items/(.+)/buy/$', 'buy', name="buy"),
	url(r'^items/(.+)/sell/$', 'sell', name="sell"),
	url(r'^heal/.*$', 'heal', name="heal"),
	url(r'^profiles/me/$', 'my_coreprofile', name="my_coreprofile"),
	url(r'^profiles/(.+)/$', 'coreprofile', name="coreprofile"),
	url(r'^skill_up/(.+)/(.+)/$', 'skill_up', name="skill_up"),
	url(r'^refill/(.+)/$', 'refill', name="refill"),
	url(r'^alliance/$', 'alliance', name="alliance"),
	#AJAX
	url(r'^fb_requests/store_ids/$', 'store_alliance_request_ids', name="store_alliance_request_ids"),
	url(r'^fb_requests/$', 'get_fb_requests', name="get_fb_requests"),
	url(r'^fb_requests/(.+)/confirm/$', 'confirm_fb_request', name="confirm_fb_request"),
	url(r'^fb_requests/(.+)/decline/$', 'decline_fb_request', name="decline_fb_request"),
)
