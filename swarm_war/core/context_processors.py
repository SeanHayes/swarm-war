# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
from datetime import datetime
from djcelery.models import PeriodicTask
import logging

#Django imports
from django.conf import settings

logger = logging.getLogger(__name__)

def tick_countdown(request):
	"Returns the time remaining for select PeriodicTasks"
	#TODO: this can be optimized to only return PeriodicTasks that contain the word "tick"
	pts = PeriodicTask.objects.select_related('crontab').all()
	now = datetime.now()
	
	d = {}
	
	task_names = settings.DW_CORE_TICK_COUNTDOWN_TASK_NAMES
	
	for pt in pts:
		if pt.name in task_names:
			val = int(pt.schedule.is_due(pt.last_run_at)[1]) if pt.last_run_at else None
			d['%s_time_remaining' % pt.name] = val
	
	if len(d) < len(task_names):
		logger.warning("Not all task names were found: %s" % d.keys())
	
	return d

def leveled_up(request):
	if request.user.is_authenticated():
		profile = request.user.coreprofile
		if profile.leveled_up:
			profile.leveled_up = False
			profile.save()
			return {'leveled_up': True}
	
	return {}

