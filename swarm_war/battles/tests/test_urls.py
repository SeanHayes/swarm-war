# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import pdb

#Django imports
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils.html import escape

#App imports
from ..models import BattleRecord, BattleProfile
from ..views import self_attack_text, attack_msg_template, won_text, lost_text, user_killed_text, opponent_killed_text, not_enough_stamina_text
from swarm_war.core.models import Item, CoreProfile
from util import BaseTestCase

class BattlesTestCase(BaseTestCase):
	def test_index(self):
		response = self.client.get(reverse('battles_index'))
		
		self.assertEqual(response.status_code, 200)
	
	def test_attack_self(self):
		us = self.user_p.stamina
		ubp_before = self.user.battleprofile
		
		response = self.client.post(reverse('attack_user', args=(self.user.id,)), follow=True)
		
		self.assertRedirects(response, reverse('battles_index'))
		self.assertContains(response, self_attack_text)
		aup = CoreProfile.objects.get(user=self.user)
		assert us == aup.stamina
		
		ubp_after = BattleProfile.objects.get(user=self.user)
		assert ubp_before == ubp_after
	
	def test_attack_not_enough_stamina(self):
		self.user_p.stamina = 0
		self.user_p.save()
		us = self.user_p.stamina
		ubp_before = self.user.battleprofile
		
		response = self.client.post(reverse('attack_user', args=(self.opponent.id,)), follow=True)
		
		self.assertRedirects(response, reverse('battles_index'))
		self.assertContains(response, escape(not_enough_stamina_text))
		aup = CoreProfile.objects.get(user=self.user)
		assert us == aup.stamina
		
		ubp_after = BattleProfile.objects.get(user=self.user)
		assert ubp_before == ubp_after
	
	def test_attack_tie(self):
		assert self.user_p.total_attack_defense['attack'] == self.opponent_p.total_attack_defense['attack']
		assert self.user_p.total_attack_defense['defense'] == self.opponent_p.total_attack_defense['defense']
		uh = self.user_p.health
		oh = self.opponent_p.health
		us = self.user_p.stamina
		assert BattleRecord.objects.count() == 0
		
		ubp = self.user.battleprofile
		obp = self.user.battleprofile
		assert ubp.attacked_and_won == 0
		assert ubp.attacked_and_lost == 0
		assert ubp.defended_and_won == 0
		assert ubp.defended_and_lost == 0
		assert obp.attacked_and_won == 0
		assert obp.attacked_and_lost == 0
		assert obp.defended_and_won == 0
		assert obp.defended_and_lost == 0
		
		response = self.client.post(reverse('attack_user', args=(self.opponent.id,)), follow=True)
		
		self.assertRedirects(response, reverse('battles_index'))
		self.assertContains(response, attack_msg_template % (won_text, 0, 0, 0, 0, '', ''))
		aup = CoreProfile.objects.get(user=self.user)
		dup = CoreProfile.objects.get(user=self.opponent)
		assert aup.health == uh
		assert dup.health == oh
		assert aup.money == CoreProfile._meta.get_field_by_name('money')[0].default()
		assert dup.money == CoreProfile._meta.get_field_by_name('money')[0].default()
		assert us - aup.stamina == 1
		
		assert BattleRecord.objects.count() == 1
		br = BattleRecord.objects.all()[0]
		assert br.attacker == self.user
		assert br.attacker_health_lost == 0
		assert br.attacker_money_lost == 0
		assert br.attacker_experience_gained == 5
		assert br.attacker_killed == False
		assert br.defender == self.opponent
		assert br.defender_health_lost == 0
		assert br.defender_money_lost == 0
		assert br.defender_experience_gained == 1
		assert br.defender_killed == False
		assert br.attacker_won == True
		
		ubp = BattleProfile.objects.get(user=self.user)
		obp = BattleProfile.objects.get(user=self.opponent)
		assert ubp.attacked_and_won == 1
		assert ubp.attacked_and_lost == 0
		assert ubp.defended_and_won == 0
		assert ubp.defended_and_lost == 0
		assert obp.attacked_and_won == 0
		assert obp.attacked_and_lost == 0
		assert obp.defended_and_won == 0
		assert obp.defended_and_lost == 1
	
	def test_attack_win(self):
		self.weapon.give_to_user(self.user)
		assert self.user_p.total_attack_defense['attack'] > self.opponent_p.total_attack_defense['attack']
		assert self.user_p.total_attack_defense['defense'] > self.opponent_p.total_attack_defense['defense']
		uh = self.user_p.health
		oh = self.opponent_p.health
		us = self.user_p.stamina
		assert BattleRecord.objects.count() == 0
		
		ubp = self.user.battleprofile
		obp = self.user.battleprofile
		assert ubp.attacked_and_won == 0
		assert ubp.attacked_and_lost == 0
		assert ubp.defended_and_won == 0
		assert ubp.defended_and_lost == 0
		assert obp.attacked_and_won == 0
		assert obp.attacked_and_lost == 0
		assert obp.defended_and_won == 0
		assert obp.defended_and_lost == 0
		
		response = self.client.post(reverse('attack_user', args=(self.opponent.id,)), follow=True)
		
		self.assertRedirects(response, reverse('battles_index'))
		#NOTE: if the algorithm changes a lot, we should just test for something less precise
		self.assertContains(response, attack_msg_template % (won_text, 10, 0, 0, 2, '', ''))
		aup = CoreProfile.objects.get(user=self.user)
		dup = CoreProfile.objects.get(user=self.opponent)
		assert aup.health == uh
		assert dup.health < oh
		assert aup.money == CoreProfile._meta.get_field_by_name('money')[0].default() + 2
		assert dup.money == CoreProfile._meta.get_field_by_name('money')[0].default() - 2
		assert us - aup.stamina == 1
		
		assert BattleRecord.objects.count() == 1
		br = BattleRecord.objects.all()[0]
		assert br.attacker == self.user
		assert br.attacker_health_lost == 0
		assert br.attacker_money_lost == 0
		assert br.attacker_experience_gained == 5
		assert br.attacker_killed == False
		assert br.defender == self.opponent
		assert br.defender_health_lost == 10
		assert br.defender_money_lost == 2
		assert br.defender_experience_gained == 1
		assert br.defender_killed == False
		assert br.attacker_won == True
		
		ubp = BattleProfile.objects.get(user=self.user)
		obp = BattleProfile.objects.get(user=self.opponent)
		assert ubp.attacked_and_won == 1
		assert ubp.attacked_and_lost == 0
		assert ubp.defended_and_won == 0
		assert ubp.defended_and_lost == 0
		assert obp.attacked_and_won == 0
		assert obp.attacked_and_lost == 0
		assert obp.defended_and_won == 0
		assert obp.defended_and_lost == 1
	
	def test_attack_lose(self):
		self.weapon.give_to_user(self.opponent)
		assert self.user_p.total_attack_defense['attack'] < self.opponent_p.total_attack_defense['attack']
		assert self.user_p.total_attack_defense['defense'] < self.opponent_p.total_attack_defense['defense']
		uh = self.user_p.health
		oh = self.opponent_p.health
		us = self.user_p.stamina
		assert BattleRecord.objects.count() == 0
		
		ubp = self.user.battleprofile
		obp = self.user.battleprofile
		assert ubp.attacked_and_won == 0
		assert ubp.attacked_and_lost == 0
		assert ubp.defended_and_won == 0
		assert ubp.defended_and_lost == 0
		assert obp.attacked_and_won == 0
		assert obp.attacked_and_lost == 0
		assert obp.defended_and_won == 0
		assert obp.defended_and_lost == 0
		
		response = self.client.post(reverse('attack_user', args=(self.opponent.id,)), follow=True)
		
		self.assertRedirects(response, reverse('battles_index'))
		self.assertContains(response, attack_msg_template % (lost_text, 0, 10, 2, 0, '', ''))
		aup = CoreProfile.objects.get(user=self.user)
		dup = CoreProfile.objects.get(user=self.opponent)
		assert aup.health < uh
		assert dup.health == oh
		assert aup.money == CoreProfile._meta.get_field_by_name('money')[0].default() - 2
		assert dup.money == CoreProfile._meta.get_field_by_name('money')[0].default() + 2
		assert us - aup.stamina == 1
		
		assert BattleRecord.objects.count() == 1
		br = BattleRecord.objects.all()[0]
		assert br.attacker == self.user
		assert br.attacker_health_lost == 10
		assert br.attacker_money_lost == 2
		assert br.attacker_experience_gained == 1
		assert br.attacker_killed == False
		assert br.defender == self.opponent
		assert br.defender_health_lost == 0
		assert br.defender_money_lost == 0
		assert br.defender_experience_gained == 5
		assert br.defender_killed == False
		assert br.attacker_won == False
		
		ubp = BattleProfile.objects.get(user=self.user)
		obp = BattleProfile.objects.get(user=self.opponent)
		assert ubp.attacked_and_won == 0
		assert ubp.attacked_and_lost == 1
		assert ubp.defended_and_won == 0
		assert ubp.defended_and_lost == 0
		assert obp.attacked_and_won == 0
		assert obp.attacked_and_lost == 0
		assert obp.defended_and_won == 1
		assert obp.defended_and_lost == 0
	
