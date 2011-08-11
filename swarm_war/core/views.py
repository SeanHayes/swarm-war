# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
from datetime import datetime
import facebook
import json
import logging
#import ipdb
import string
import urllib

#Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage
from django.core.urlresolvers import reverse
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import list_detail

#App imports
from . import parse_signed_request
from forms import BuyItemForm, SellItemForm, RefillForm
from models import Item, UserItem, CoreProfile, FacebookRequest

logger = logging.getLogger(__name__)

# Create your views here.

#TODO: try to only csrf exempt for facebook.com urls
@csrf_exempt
def canvas(request):
	"""
	The Facebook canvas page.
	
	We can't use straight FlatPages since it can't handle the POST Facebook sends
	to canvas pages, plus some extra processing might need to be done, so we'll
	just use a custom view.
	"""
	#TESTME
	#TODO: maybe some of this should be moved to a middleware, so that it'll
	#work on any page request and more FB integration can be grouped together.
	#logger.debug('User: %s' % request.user)
	if request.method == 'POST':
		#need to check for signed_request
		#logger.debug('Canvas was POSTed to')
		data = parse_signed_request(request.POST['signed_request']) if 'signed_request' in request.POST else None
		#logger.debug('Here\'s what Facebook sent us: %s' % data)
		if data is not None:
			#user_id is in data when a user who authorized the app visits from FB.
			#otherwise they haven't authorized the app, in which case they are
			#definitely not the currently logged in user.
			should_logout = True
			if 'user_id' in data:
				#logger.debug('user_id: %s' % data['user_id'])
				try:
					#check to make sure the FB user matches the currently logged in user
					user_from_fb = authenticate(uid=data['user_id'])
					if user_from_fb is not None:
						#logger.debug('retrieved user_from_fb: %s' % user_from_fb)
						
						#if they're not the same but the correct user was found in the DB, log that user in
						if user_from_fb.id != request.user.id:
							#the user_id came from a secure signed request from Facebook, so this is safe
							login(request, user_from_fb)
							messages.success(request, 'Successfully logged in!')
							logger.debug('logged in FB user')
						
						#update oauth token in case the one we have is stale.
						#Logging a user in without making sure we have a usable API token would be bad.
						fb = user_from_fb.facebook
						if 'oauth_token' in data and fb.access_token != data['oauth_token']:
								#logger.debug('updating oauth_token')
								fb.access_token = data['oauth_token']
								fb.save()
						
						should_logout = False
					#else:
					#	logger.debug('no user could be retrieved')
				except Exception as e:
					logger.error(e)
			
			if should_logout and request.user.is_authenticated():
				#logger.debug('logging out user')
				logout(request)
	
	cookies = {}
	
	#logger.debug('User: %s' % request.user)
	#handle accepted Facebook requests
	if 'request_ids' in request.GET:
		request_ids = request.GET['request_ids']
		
		if not request.user.is_authenticated():
			#if the user is not authenticated, set the ids in a cookie for retrieval later
			cookies['request_ids'] = request_ids
		else:
			for fbr in FacebookRequest.objects.filter(id__in=request_ids.split(',')):
				try:
					fbr = fbr.as_leaf_class()
					fbr.confirm(request.user)
					messages.success(request, u'Confirmed request from %s' % fbr.user)
				except Exception as e:
					msg = 'Could not confirm request, the following error occurred: %s' % e
					logger.error(msg)
					messages.error(request, msg)
	
	ref = request.GET.get('ref', '')
	auto_check_for_requests = 'request_ids' in request.GET or ref == 'bookmarks'
	
	response = render(request, 'core/canvas.html', {
			'auto_check_for_requests': auto_check_for_requests,
		}
	)
	for key in cookies:
		response.set_cookie(key, cookies[key])
	
	return response

@login_required
def my_coreprofile(request):
	return coreprofile(request, None)

def coreprofile(request, user_id):
	
	user = User.objects.select_related('coreprofile', 'facebook').get(id=user_id) if user_id is not None else request.user
	
	uprof = user.coreprofile
	
	extra_context = {
		'owns_profile': user == request.user,
		'can_skill_up_1': False,
		'can_skill_up_5': False,
		'profile_user': user,
	}
	if extra_context['owns_profile'] and uprof.attribute_points >= 1:
		extra_context['can_skill_up_1'] = True
		if uprof.attribute_points > 5:
			extra_context['can_skill_up_5'] = True
	
	return list_detail.object_detail(
		request,
		CoreProfile.objects.all(),
		object_id=uprof.id,
		template_name='core/coreprofile.html',
		extra_context=extra_context
	)

@login_required
def skill_up(request, attr, num):
	"Increases skill points such as attack, defense, max health, etc."
	if request.method == 'POST':
		try:
			uprof = request.user.coreprofile
			uprof.skill_up(attr, long(num))
			messages.success(request, 'Skill level increased!')
		except Exception as e:
			messages.error(request, e)
	
	return HttpResponseRedirect(reverse('my_coreprofile'))

@login_required
def heal(request):
	"Heals a user if he or she has enough money."
	if request.method == 'POST':
		uprof = request.user.coreprofile
		if uprof.health < uprof.max_health:
			if uprof.total_money > 0:
				cost = uprof.cost_to_heal()
				amt_to_heal = uprof.max_health - uprof.health
				fraction = 1
				if cost > uprof.total_money:
					amt_to_heal = int(amt_to_heal * (float(uprof.total_money)/cost))
					cost = uprof.total_money
				
				if amt_to_heal < 1:
					messages.error(request, 'You don\'t have enough money to heal.')
				else:
					uprof.auto_charge(cost, save=False)
					uprof.health = F('health') + amt_to_heal
					uprof.save()
					messages.success(request, '%d health restored!' % amt_to_heal)
			else:
				messages.error(request, 'You can\'t heal because you don\'t have any money.')
		else:
			messages.error(request, 'You can\'t heal because your health is at maximum.')
	
	next = None
	if 'next' in request.GET:
		next = request.GET['next']
	else:
		next = reverse('my_coreprofile')
	
	return HttpResponseRedirect(next)

@login_required
def inventory(request):
	"List of Items a player has."
	classes = Item.objects.get_inventory_item_classes()
	l = [(string.capwords(c._meta.verbose_name_plural), c.get_m2m_class().objects.get_inventory_useritems(request.user, c)) for c in classes]
	
	return render(request, 'core/inventory.html', {
			'class_list': l,
			'sell_form': SellItemForm(),
		}
	)

@login_required
def store(request):
	"List of Items a player can buy."
	classes = Item.objects.get_store_item_classes()
	l = [(string.capwords(c._meta.verbose_name_plural), c.objects.get_store_items()) for c in classes]
	
	return render(request, 'core/store.html', {
			'class_list': l,
			'buy_form': BuyItemForm(),
			'refill_data': CoreProfile.REFILL_DATA,
		}
	)

@login_required
def refill(request, attr):
	"Refill an attribute"
	if request.method == "POST":
		form = RefillForm({'attr': attr})
		
		if form.is_valid():
			attr = form.cleaned_data['attr']
			try:
				request.user.coreprofile.refill(attr)
				messages.success(request, 'Successfully refilled %s!' % attr)
			except Exception as e:
				messages.error(request, e)
		else:
			messages.error(request, 'Attribute not recognized: %s' % form.errors)
	
	return HttpResponseRedirect(reverse('store'))

@login_required
def buy(request, id):
	"Buy an Item."
	
	if request.method == "POST":
		item = Item.objects.get(id=id)
		form = BuyItemForm(request.POST)
		quantity = 1
		
		if form.is_valid():
			quantity = form.cleaned_data['quantity']
		#logger.debug('quantity: %s' % quantity)
		try:
			item.give_to_user(request.user, quantity=quantity)
			messages.success(request, 'Purchase successful!')
		except Exception as e:
			messages.error(request, e)
	
	return HttpResponseRedirect(reverse('store'))

@login_required
def sell(request, id):
	"Sell an Item."
	
	if request.method == "POST":
		ui = UserItem.objects.get(id=id, user=request.user)
		form = SellItemForm(request.POST)
		quantity = 1
		if form.is_valid():
			quantity = form.cleaned_data['quantity']
		
		try:
			ui.sell(quantity)
			messages.success(request, 'Sale successful!')
		except Exception as e:
			messages.error(request, e)
	
	return HttpResponseRedirect(reverse('inventory'))

@login_required
def alliance(request):
	"Shows alliance members, has a dialog for inviting new members."
	prof = request.user.coreprofile
	
	return list_detail.object_list(
		request,
		queryset = prof.allies.all(),
		template_name='core/alliance.html',
		extra_context={'invite_message': settings.DW_CORE_ALLIANCE_INVITE_TEXT}
	)

@csrf_exempt
@login_required
def store_alliance_request_ids(request):
	try:
		if request.method == "POST":
			ids = json.loads(request.raw_post_data)
		
			#TODO: maybe this ought to be done in Celery
			FacebookRequest.objects.create_many(ids, user=request.user, date=datetime.now())
			
			return HttpResponse('', mimetype="text/plain")
		else:
			return HttpResponseNotAllowed(['POST'])
	except Exception as e:
		logger.error(e)
		return HttpResponseBadRequest('The following error occurred: %s' % e, mimetype="text/plain")

def get_fb_requests(request):
	user = request.user
	try:
		if user.is_authenticated():
			graph = facebook.GraphAPI(user.facebook.access_token)
			response = graph.request('/me/apprequests/')
			#response = json.loads(response)
			#logger.debug(response)
			req_ids = [data['id'] for data in response['data']]
		else:
			logger.debug('COOKIES: %s' % request.COOKIES)
			req_ids = request.COOKIES['request_ids'].split(',') if 'request_ids' in request.COOKIES else []
		
		fb_req_objects = FacebookRequest.objects.filter(id__in=req_ids)
		
		if len(req_ids) > len(fb_req_objects):
			fb_req_object_ids = [req.id for req in fb_req_objects]
			absent_ids = [req_id for req_id in req_ids if req_id not in fb_req_object_ids]
			logger.warning('The following ids could not be found in the DB: %s' % absent_ids)
			if request.user.is_authenticated():
				try:
					graph = facebook.GraphAPI(request.user.facebook.access_token)
					for absent_id in absent_ids:
						#there's bugs in the FB SDK and API that causes this to randomly throw an error
						graph.delete_object(absent_id)
				except Exception as e:
					logger.debug(e)
		
		fb_reqs = [
			{
				'id': fb_req.id,
				'html': fb_req.as_leaf_class().html(),
				'confirm_url': reverse('confirm_fb_request', args=[fb_req.id]),
				'decline_url': reverse('decline_fb_request', args=[fb_req.id]),
			} for fb_req in fb_req_objects
		]
		
		d = {
			'requests': fb_reqs,
			'logged_in': user.is_authenticated(),
		}
		
		return HttpResponse(json.dumps(d), mimetype="text/json")
	except Exception as e:
		logger.error(e)
		return HttpResponseBadRequest('The following error occurred: %s' % e, mimetype="text/plain")

@csrf_exempt
@login_required
def confirm_fb_request(request, fb_req_id):
	if request.method == "POST":
		#FIXME: this is hackable, should store recipient id on model
		fb_req = FacebookRequest.objects.get(id=fb_req_id)
		fb_req.confirm(request.user)
		
		return HttpResponse('', mimetype="text/plain")
	else:
		return HttpResponseNotAllowed(['POST'])

@csrf_exempt
@login_required
def decline_fb_request(request, fb_req_id):
	if request.method == "POST":
		#FIXME: this is hackable, should store recipient id on model
		fb_req = FacebookRequest.objects.get(id=fb_req_id)
		fb_req.decline()
		
		return HttpResponse('', mimetype="text/plain")
	else:
		return HttpResponseNotAllowed(['POST'])

