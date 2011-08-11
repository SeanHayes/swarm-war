# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import logging

#Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.generic import list_detail

#App imports
from models import *

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def index(request):
	"Redirect to last viewed area"
	#get last viewed area
	area = request.user.missionprofile.last_area_viewed
	if area is None:
		try:
			area = Area.objects.all()[0]
		except IndexError:
			return render_to_response('missions/no_areas.html', context_instance=RequestContext(request))
	return HttpResponseRedirect(reverse('area_view', args=[area.id]))

@login_required
def view(request, area_id):
	"Shows a mission list for an area"
	user = request.user
	profile = user.missionprofile
	#give first mission to user if it exists
	if UserMission.objects.filter(user=user).count() == 0:
		try:
			Mission.objects.all()[0].give_to_user(request.user)
		except:
			pass
	area = Area.objects.get(id=area_id)
	#update last area viewed
	if(profile.last_area_viewed != area):
		profile.last_area_viewed = area
		profile.save()
	
	return list_detail.object_list(
		request,
		queryset = UserMission.objects.filter(user=user, item__mission__area=area_id).order_by('item__order'),
		extra_context={
			'area_list': Area.objects.all(),
			'current_area_id': long(area_id)
		}
	)


@login_required
def do_mission(request, mission_id):
	"Do mission, reducing a player's energy and increasing mission progress"
	usermission = UserMission.objects.select_related('item__mission__area').get(item__mission__id=mission_id, user=request.user)
	
	if request.method == "POST":
		try:
			items_received = usermission.do_mission()
			messages.success(request, u'Mission completed!')
			logger.debug(items_received)
			for item in items_received:
				logger.debug(u'You received: %s' % item)
				messages.success(request, u'You received: %s' % item)
		except Exception as e:
			#FIXME: only show certain errors
			messages.error(request, 'Could not do mission: %s' % e)
		#TODO: need to show feedback (items won, etc. on page load)
	area_id = usermission.item.mission.area.id
	return HttpResponseRedirect('%s#mission_%s' % (reverse('area_view', args=[area_id]), mission_id))
	
