# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
from celery.decorators import task
import facebook
import logging

#Django imports
from django.conf import settings
from django.db.models import F
from django.db.models.signals import post_save

#App imports
from models import CoreProfile
from django_facebook_oauth.models import FacebookUser

logger = logging.getLogger(__name__)

@task()
def energy_tick(*args, **kwargs):
	"Increases energy for all users."
	logger = energy_tick.get_logger(**kwargs)
	logger.debug('energy_tick')
	#update users who will still be below maximum after increase
	CoreProfile.objects.filter(energy__lt=F('max_energy')-settings.DW_CORE_ENERGY_PER_TICK).update(energy=F('energy')+settings.DW_CORE_ENERGY_PER_TICK)
	#bring other users up to maximum
	CoreProfile.objects.filter(energy__gte=F('max_energy')-settings.DW_CORE_ENERGY_PER_TICK, energy__lt=F('max_energy')).update(energy=F('max_energy'))

@task()
def stamina_tick(*args, **kwargs):
	"Increases stamina for all users."
	logger = stamina_tick.get_logger(**kwargs)
	logger.debug('stamina_tick')
	#update users who will still be below maximum after increase
	CoreProfile.objects.filter(stamina__lt=F('max_stamina')-settings.DW_CORE_STAMINA_PER_TICK).update(stamina=F('stamina')+settings.DW_CORE_STAMINA_PER_TICK)
	#bring other users up to maximum
	CoreProfile.objects.filter(stamina__gte=F('max_stamina')-settings.DW_CORE_STAMINA_PER_TICK, stamina__lt=F('max_stamina')).update(stamina=F('max_stamina'))

@task()
def health_tick(*args, **kwargs):
	"Increases health for all users."
	logger = health_tick.get_logger(**kwargs)
	logger.debug('health_tick')
	#update users who will still be below maximum after increase
	CoreProfile.objects.filter(health__lt=F('max_health')-settings.DW_CORE_HEALTH_PER_TICK).update(health=F('health')+settings.DW_CORE_HEALTH_PER_TICK)
	#bring other users up to maximum
	CoreProfile.objects.filter(health__gte=F('max_health')-settings.DW_CORE_HEALTH_PER_TICK, health__lt=F('max_health')).update(health=F('max_health'))

@task()
def facebook_post(fb_profile_id, msg_key, *args, **kwargs):
	logger = facebook_post.get_logger(**kwargs)
	logger.debug('facebook_post')
	fb_profile = FacebookUser.objects.select_related('user').get(id=fb_profile_id)
	user = fb_profile.user
	
	format_d = {
		'name': user.first_name if user.first_name is not None else user.username
	}
	
	d = settings.DW_CORE_FB_POST_DICT[msg_key]
	attachment = {}
	for key in d:
		attachment[key] = d[key] % format_d
	try:
		graph = facebook.GraphAPI(fb_profile.access_token)
		message = attachment.pop('message')
		post_id = graph.put_wall_post(message, attachment=attachment)
		logger.debug('post_id: %s' % post_id)
	except Exception as e:
		logger.error(e)

#FIXME: Does this need to be moved to models.py?
def facebookuser_post_save_handler(sender, instance, created, **kwargs):
	if created:
		facebook_post.apply_async(args=(instance.id, 'profile_created'))
post_save.connect(facebookuser_post_save_handler, sender=FacebookUser)
