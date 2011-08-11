# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import base64
import hashlib
import hmac
import json
import logging
import string

#Django imports
from django.conf import settings

logger = logging.getLogger(__name__)

#ported from: https://github.com/facebook/credits-api-sample/blob/master/callback.php
def parse_signed_request(signed_request):
	"Parses a signed request from Facebook"
	secret = settings.FACEBOOK_SECRET_KEY
	#logger.debug('signed_request: %s' % signed_request)
	encoded_sig, payload = signed_request.split('.', 2)
	
	#decode the data
	sig = base64_url_decode(encoded_sig)
	s = base64_url_decode(payload)
	logger.debug(s)
	data = json.loads(s)
	
	if data['algorithm'].upper() != 'HMAC-SHA256':
		logger.error('Unknown algorithm. Expected HMAC-SHA256')
		return None
	
	#check signature
	#expected_sig = hash_hmac('sha256', payload, secret, raw = true)
	expected_sig = hmac.new(secret, payload, hashlib.sha256).digest()
	
	if sig != expected_sig:
		logger.error('Bad Signed JSON signature: got %s, expected %s' % (sig, expected_sig))
		return None
	
	return data;

def base64_url_decode(s_input):
	#logger.debug(s_input)
	#logger.debug('length: %s' % len(s_input))
	i = 4-(len(s_input) % 4)
	s_input += '='*i
	#logger.debug(s_input)
	#logger.debug('length: %s' % len(s_input))
	return base64.urlsafe_b64decode(s_input.encode('ascii'))
