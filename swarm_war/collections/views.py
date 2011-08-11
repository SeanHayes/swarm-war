# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import logging
import pdb

#Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

#App imports
from ..core.models import UserItem
from models import Collection

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def collections(request):
	"List of Collections."
	user = request.user
	cs = Collection.objects.all()
	ui_q = {}
	for ui in UserItem.objects.filter(user=user):
		ui_q[ui.item.id] = ui.quantity
	c_can_redeem = []
	for c in cs:
		if c.has_enough_items(user):
			c_can_redeem.append(c.id)
	
	#logger.debug(ui_q)
	return render(request, 'collections/index.html',
		{
			'object_list': cs,
			'useritem_quantities': ui_q,
			'can_redeem': c_can_redeem
		}
	)

@login_required
def redeem_collection(request, c_id):
	"Redeem collection."
	if request.method == "POST":
		try:
			#FIXME: use form to clean+validate input
			c = Collection.objects.get(id=c_id)
			prize = c.redeem(request.user)
			messages.success(request, 'You got a %s!' % prize)
		except Collection.DoesNotExist:
			messages.error(request, 'Collection doesn\'t exist.')
		except Exception as e:
			messages.error(request, e)
	
	return HttpResponseRedirect(reverse('collections'))

