# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import json
import logging

#Django imports
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import list_detail

#App imports
from models import Listing, PurchaseRecord
from swarm_war.core import parse_signed_request
from swarm_war.core.models import CoreProfile

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def index(request):
	return list_detail.object_list(
		request,
		queryset = Listing.objects.all()
	)

@csrf_exempt
def fb_callback(request):
	#Ported from https://github.com/facebook/credits-api-sample/blob/master/callback.php
	
	#prepare the return data array
	data = {'content': {},}
	
	#parse signed data
	try:
		logger.debug('FACEBOOK_SECRET_KEY: %s' % settings.FACEBOOK_SECRET_KEY)
		logger.debug('signed_request: %s' % request.REQUEST['signed_request'])
		parsed_request = parse_signed_request(request.REQUEST['signed_request'])
	except Exception as e:
		logger.error(e)
		parsed_request = None
	logger.debug('parsed_request: %s' % parsed_request)
	
	if parsed_request == None:
		return HttpResponseBadRequest()
	
	payload = parsed_request['credits']
	
	#retrieve all params passed in
	func = request.REQUEST['method']
	order_id = payload['order_id']
	
	logger.debug('func: %s' % func)
	if func == 'payments_status_update':
		status = payload['status']
		logger.debug('order_details: %s' % payload['order_details'])
		#Facebook double encodes their JSON strings, so that some inner values are strings instead of objects.
		#We have to conditionally fix it, in case they fix it on their end in the future.
		if type(payload['order_details']) != dict:
			payload['order_details'] = json.loads(payload['order_details'])
		receiver_uid = payload['order_details']['receiver']
		receiver_p = None
		try:
			#in the future, Facebook will let users buy items for friends so
			#the receiver might not be the buyer, but who knows if they'll
			#restrict it to friends who also use the same app
			receiver_p = CoreProfile.objects.select_related('user').get(user__facebook__uid=receiver_uid)
		except CoreProfile.DoesNotExist as e:
			#return an error in case user can't be found
			logger.error(e)
			return HttpResponseBadRequest()
		items = payload['order_details']['items']
		item_ids = [item['item_id'] for item in items]
		listings = Listing.objects.filter(id__in=item_ids)
		
		if len(items) != len(listings):
			#return an error in case items couldn't be found.
			logger.error('FB requested %s items, found %s. IDs were: %s' % (len(items), len(listings), item_ids))
			return HttpResponseBadRequest()
		
		#write your logic here, determine the state you wanna move to
		if status == 'placed':
			next_state = 'settled'
			data['content']['status'] = next_state
		#Facebook will callback for a 3rd time to confirm the status as settled,
		#which is when we should give the item to the receiver
		elif status == 'settled':
			total_credits = sum([listing.num_game_credits for listing in listings])
			receiver_p.credits += total_credits
			receiver_p.save()
			pr = PurchaseRecord(receiver=receiver_p.user)
			pr.save()
			pr.listings.add(*listings)
			pr.save()
			
		#compose returning data array_change_key_case
		data['content']['order_id'] = order_id
	
	elif func == 'payments_get_items':
		#remove escape characters
		#order_info = stripcslashes(payload['order_info'])#is this needed in Python?
		#fixing the JSON again
		if type(payload['order_info']) != dict:
			payload['order_info'] = json.loads(payload['order_info'])
		order_info = payload['order_info']
		logger.debug('order_info: %s' % order_info)
		
		#In the sample credits application we allow the developer to enter the
		#information for easy testing. Please note that this information can be
		#modified by the user if not verified by your callback. When using
		#credits in a production environment be sure to pass an order ID and
		#contruct item information in the callback, rather than passing it
		#from the parent call in order_info.
		#order_info = json.loads(order_info)
		try:
			listing = Listing.objects.get(id=order_info)
		except Listing.DoesNotExist as e:
			logger.error(e)
			return HttpResponseNotFound()
		except Exception as e:
			logger.error(e)
			return HttpResponseBadRequest()
		item = {}
		item['item_id'] = listing.id
		item['title'] = listing.get_title()
		item['price'] = listing.num_fb_credits
		item['description'] = listing.get_description()
		item['image_url'] = listing.image_url
		item['product_url'] = listing.product_url
		
		#When will we ever be storing URLs without a protocol?
		#for url fields, if not prefixed by http://, prefix them
		#url_key =['product_url', 'image_url']
		#for key in url_key:
		#	if item[key][0, 7] != 'http://':
		#		item[key] = 'http://'+item[key];
		
		#prefix test-mode
		if 'test_mode' in payload:
			update_keys = ['title', 'description']
			for key in update_keys:
				item[key] = '[Test Mode] '+item[key]
		
		#Put the associate array of item details in an array, and return in the
		#'content' portion of the callback payload.
		data['content'] = [item]
	
	#required by api_fetch_response()
	data['method'] = func
	
	logger.debug('data: %s' % data)
	
	#send data back
	resp = HttpResponse(json.dumps(data), mimetype="text/json")
	return resp

