# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import logging

#Django imports
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Sum
from django.http import HttpResponseNotFound
from django.shortcuts import render

#App imports
from ..core.models import Item
from ..missions.models import Mission

logger = logging.getLogger(__name__)

# Create your views here.

uo = User.objects

def get_list(qs, relevant_value=None):
	if relevant_value is not None:
		qs = qs.annotate(relevant_value=relevant_value).filter(relevant_value__isnull=False)
	return qs.order_by('-relevant_value')

def get_player_leaderboard():
	return {
		'Most Experience': get_list(uo.select_related('coreprofile').extra(select={'relevant_value': '"core_coreprofile"."experience"'})),
		'Most Money Saved': get_list(uo.select_related('coreprofile').extra(select={'relevant_value': '"core_coreprofile"."banked_money"'})),
		'Most Items Aquired': get_list(uo.filter(useritem__item__content_type=ContentType.objects.get_for_model(Item)), Sum('useritem__quantity')),
		'Most Types of Items Aquired': get_list(uo.filter(useritem__item__content_type=ContentType.objects.get_for_model(Item)), Count('useritem')),
		'Most Missions Done': get_list(uo, Sum('useritem__usermission__times_succeeded')),
		'Most Missions Unlocked': get_list(uo.filter(useritem__item__content_type=ContentType.objects.get_for_model(Mission)), Count('useritem')),#Count('useritem__usermission') doesn't work, counts all useritems
		'Most Alliance Members': get_list(uo, Count('coreprofile__allies')),
		#'Least Killed': User.objects.annotate(relevant_value=Count('battleprofile__killed')).order_by('-relevant_value'),
		#'Most Killed': User.objects.annotate(relevant_value=Count('battleprofile__killed')).order_by('-relevant_value'),
		#'Least Kills': User.objects.annotate(relevant_value=Count('battleprofile__kills')).order_by('-relevant_value'),
		#'Most Kills': User.objects.annotate(relevant_value=Count('battleprofile__kills')).order_by('-relevant_value'),
	}

def index(request):
	return render(request, "leaderboard/index.html",
		{
			"leaderboard": get_player_leaderboard(),
			"slice_str": '0:%s' % settings.DW_LEADERBOARD_NUM_TOP_USERS,
			"num_top_users": settings.DW_LEADERBOARD_NUM_TOP_USERS,
			"enable_category_pages": settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES,
		}
	)

def view(request, category):
	if not settings.DW_LEADERBOARD_ENABLE_CATEGORY_PAGES:
		return HttpResponseNotFound()
	
	qs = get_player_leaderboard().get(category, None)
	
	if qs is None:
		return HttpResponseNotFound()
	
	return render(request, "leaderboard/view.html",
		{
			"category": category,
			"qs": qs,
		}
	)
