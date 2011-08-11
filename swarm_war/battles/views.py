# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import logging
import pdb

#Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.views.generic import list_detail

#App imports
from swarm_war.core.models import CoreProfile
from models import BattleRecord, BattleProfile

logger = logging.getLogger(__name__)

# Create your views here.
self_attack_text = 'You cannot attack yourself.'
attack_msg_template = 'You %s! Dealt %s damage, lost %s health, lost %s money, gained %s money.%s%s'
won_text = 'won'
lost_text = 'lost'
user_killed_text = 'You were killed!'
opponent_killed_text = 'You killed your opponent!'
not_enough_stamina_text = 'You don\'t have enough stamina.'

@login_required
def index(request):
	brs = BattleRecord.objects.filter(Q(attacker=request.user) | Q(defender=request.user))
	#get random list of users
	return list_detail.object_list(
		request,
		#FIXME: I think the same 20 people will get cached every time by dqc
		queryset = CoreProfile.objects.exclude(user=request.user).order_by('?')[:20],
		extra_context={'battlerecords': brs},
		template_name='battles/index.html'
	)

@login_required
def attack_user(request, defender_id):
	defender_id = long(defender_id)
	
	if request.user.id == defender_id:
		messages.error(request, self_attack_text)
	else:
		attacker = request.user.coreprofile
		
		if attacker.stamina <= 1:
			messages.error(request, not_enough_stamina_text)
		else:
			attacker.stamina -= 1
			
			defender_u = User.objects.get(id=defender_id)
			defender = defender_u.coreprofile
			
			attacker_bp = request.user.battleprofile
			defender_bp = defender_u.battleprofile
			
			#CLEANUP: there's a lot of code duplication here. Any way to reduce it?
			#TODO: send opponent notification
			attacker_ad = attacker.total_attack_defense
			defender_ad = defender.total_attack_defense
			logger.debug(attacker_ad)
			logger.debug(defender_ad)
			#main attack
			defender_health_lost = 0 if attacker_ad['attack'] is 0 else long(attacker_ad['attack'] * (1.0-float(defender_ad['defense'])/attacker_ad['attack']))
			#disallows "healing"
			if defender_health_lost < 0:
				defender_health_lost = 0
			#proportional to percent health lost
			defender_money_lost = long((float(defender_health_lost)/defender.max_health) * defender.money)
			
			#counter attack
			attacker_health_lost = 0 if defender_ad['attack'] is 0 else long(defender_ad['attack'] * (1.0-float(attacker_ad['defense'])/defender_ad['attack']))
			if attacker_health_lost < 0:
				attacker_health_lost = 0
			attacker_money_lost = long((float(attacker_health_lost)/attacker.max_health) * attacker.money)
			
			defender_experience = 1
			attacker_experience = 1
			
			#attackers have slight advantage
			attacker_won = True
			if attacker_health_lost > defender_health_lost:
				attacker_won = False
				defender_experience = 5
			else:
				attacker_experience = 5
			
			if attacker_won:
				attacker_bp.attacked_and_won += 1
				defender_bp.defended_and_lost += 1
			else:
				attacker_bp.attacked_and_lost += 1
				defender_bp.defended_and_won += 1
			
			attacker_killed = False
			attacker_money_new = attacker.money - attacker_money_lost + defender_money_lost
			if attacker_health_lost > 0 or attacker_money_new != attacker.money:
				attacker.health -= attacker_health_lost
				if attacker.health <= 0:
					attacker_killed = True
					attacker_bp.killed += 1
					defender_bp.kills += 1
					attacker.health = 0
				attacker.money = attacker_money_new
			attacker.experience += attacker_experience
			attacker.save()
			
			defender_killed = False
			defender_money_new = defender.money - defender_money_lost + attacker_money_lost
			if defender_health_lost > 0 or defender_money_new != defender.money:
				defender.health -= defender_health_lost
				if defender.health <= 0:
					defender_killed = True
					defender_bp.killed += 1
					attacker_bp.kills += 1
					defender.health = 0
				defender.money = defender_money_new
			defender.experience += defender_experience
			defender.save()
			
			#store battle results in DB (so defender can see later)
			br = BattleRecord(
				attacker = attacker.user,
				attacker_health_lost = attacker_health_lost,
				attacker_money_lost = attacker_money_lost,
				attacker_experience_gained = attacker_experience,
				attacker_killed = attacker_killed,
				defender = defender.user,
				defender_health_lost = defender_health_lost,
				defender_money_lost = defender_money_lost,
				defender_experience_gained = defender_experience,
				defender_killed = defender_killed,
				attacker_won = attacker_won
			)
			br.save()
			
			attacker_bp.save()
			defender_bp.save()
			
			#add results to message
			msg = attack_msg_template % (
				won_text if attacker_won else lost_text,
				defender_health_lost,
				attacker_health_lost,
				attacker_money_lost,
				defender_money_lost,
				user_killed_text if attacker_killed else '',
				opponent_killed_text if defender_killed else '',
			)
			messages.success(request, msg)
	
	return HttpResponseRedirect(reverse('battles_index'))

