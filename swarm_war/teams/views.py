# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
from datetime import datetime
import json
import logging
#import ipdb

#Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import list_detail
from django.utils import safestring

#App imports
from forms import TeamForm
from models import Team, TeamProfile, TeamFacebookRequest, MAX_TEAM_SIZE

logger = logging.getLogger(__name__)

# Create your views here.

def index(request):
	return list_detail.object_list(
		request,
		queryset = Team.objects.all(),
		template_name='teams/index.html'
	)

def view(request, team_id):
	try:
		team = Team.objects.select_related('members').get(id=team_id)
	except Team.DoesNotExist:
		return HttpResponseNotFound()
	on_team = True if request.user.id in [tp.user_id for tp in team.members.all()] else False
	
	members = team.members.all()
	
	return render(request, 'teams/view.html',
		{
			'object': team,
			'members': members,
			'can_invite': on_team and len(members) < MAX_TEAM_SIZE,
			'MAX_TEAM_SIZE': MAX_TEAM_SIZE,
			'on_team': on_team,
			'invite_message': settings.DW_TEAMS_INVITE_TEXT % team.name,
		}
	)

NOT_ON_TEAM_MSG = lambda: safestring.mark_safe(u'You are not on a team. Find one to join or <a href="%s">create a new team</a> to invite your friends to!' % reverse('teams_create'))

@login_required
def view_my_team(request):
	tp = request.user.teamprofile
	if tp.team_id is None:
		messages.error(request, NOT_ON_TEAM_MSG())
		return HttpResponseRedirect(reverse('teams_index'))
	else:
		return HttpResponseRedirect(reverse('teams_view', args=[tp.team_id]))

@login_required
def create(request):
	if request.method == 'POST':
		form = TeamForm(request.POST)
		
		if form.is_valid():
			profile = request.user.teamprofile
			team = profile.create_team(form.cleaned_data['name'])
			return HttpResponseRedirect(reverse('teams_view', args=[team.id]))
	else:
		form = TeamForm()
	
	return render_to_response("teams/add.html", {
			"form": form,
		},
		context_instance=RequestContext(request)
	)

@login_required
def leave(request):
	profile = request.user.teamprofile
	if request.method == 'POST':
		profile.leave_team()
		
		return HttpResponseRedirect(reverse('teams_index'))
	else:
		return HttpResponseRedirect(reverse('teams_view', args=[profile.team.id]))

@login_required
def kick_out(request, user_id):
	profile = request.user.teamprofile
	if request.method == 'POST':
		try:
			user = User.objects.get(id=user_id)
			profile.kick_out(user)
			messages.success(request, 'Kicked out %s' % user)
		except Exception as e:
			messages.error(request, e)
	
	if profile.team is not None:
		return HttpResponseRedirect(reverse('teams_view', args=[profile.team.id]))
	else:
		return HttpResponseRedirect(reverse('teams_index'))

@login_required
def become_leader(request):
	profile = request.user.teamprofile
	
	if request.method == 'POST':
		try:
			profile.become_leader()
		except Exception as e:
			messages.error(request, e)
	
	if profile.team is not None:
		return HttpResponseRedirect(reverse('teams_view', args=[profile.team.id]))
	else:
		return HttpResponseRedirect(reverse('teams_index'))

@csrf_exempt
@login_required
def store_request_ids(request, team_id):
	try:
		ids = json.loads(request.raw_post_data)
		
		team = Team.objects.get(id=team_id)
		
		#TODO: this ought to be done in Celery
		TeamFacebookRequest.objects.create_many(ids, user=request.user, date=datetime.now(), team=team)
		
		return HttpResponse('', mimetype="text/plain")
	except Exception as e:
		logger.error(e)
		return HttpResponseBadRequest('The following error occurred: %s' % e, mimetype="text/plain")

