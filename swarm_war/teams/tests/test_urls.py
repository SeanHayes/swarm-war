# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
#import ipdb

#Django imports
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

#App imports
from ..exceptions import TeamAlreadyExistsError, NotOnATeamError, TeamAlreadyHasALeaderError, NotALeaderError, NotOnSameTeamError
from ..forms import TeamForm
from ..models import Team, TeamProfile, TeamFacebookRequest
from ..views import NOT_ON_TEAM_MSG

#Test imports
from util import BaseTestCase

class IndexTestCase(BaseTestCase):
	def test_empty(self):
		response = self.client.get(reverse('teams_index'))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "There are no teams.")
		self.assertNotContains(response, self.team1.name)
		self.assertNotContains(response, self.team2.name)
	
	def test_non_empty(self):
		self.team1.save()
		self.team2.save()
		
		response = self.client.get(reverse('teams_index'))
		
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, "There are no teams.")
		self.assertContains(response, self.team1.name)
		self.assertContains(response, self.team2.name)

class ViewTestCase(BaseTestCase):
	def test_does_not_exist(self):
		response = self.client.get(reverse('teams_view', args=(1,)))
		
		self.assertEqual(response.status_code, 404)
	
	def test_exists_has_leave_button(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		
		response = self.client.get(reverse('teams_view', args=(self.team1.id,)))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.team1.name)
		self.assertContains(response, self.user1.username)
		self.assertNotContains(response, self.user2.username)
		self.assertContains(response, reverse('teams_leave'))
	
	def test_exists_has_no_leader(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		
		response = self.client.get(reverse('teams_view', args=(self.team1.id,)))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.team1.name)
		self.assertContains(response, self.user1.username)
		self.assertNotContains(response, self.user2.username)
		#self.assertContains(response, reverse('teams_join', args=(self.team1.id]))
		self.assertNotContains(response, '(Leader)')
		self.assertContains(response, reverse('teams_become_leader'))
	
	def test_exists_has_leader(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		self.user1.teamprofile.leader = True
		self.user1.teamprofile.save()
		
		response = self.client.get(reverse('teams_view', args=(self.team1.id,)))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.team1.name)
		self.assertContains(response, self.user1.username)
		self.assertNotContains(response, self.user2.username)
		#self.assertContains(response, reverse('teams_join', args=(self.team1.id]))
		self.assertContains(response, '(Leader)')
		self.assertNotContains(response, reverse('teams_become_leader'))
	
	def test_exists_team_full(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		self.user2.teamprofile.join_team(self.team1)
		user3 = User.objects.create_user('baddie3', 'baddie3@example.com', 'Teletubies')
		user4 = User.objects.create_user('baddie4', 'baddie4@example.com', 'Teletubies')
		user5 = User.objects.create_user('baddie5', 'baddie5@example.com', 'Teletubies')
		user6 = User.objects.create_user('baddie6', 'baddie6@example.com', 'Teletubies')
		user7 = User.objects.create_user('baddie7', 'baddie7@example.com', 'Teletubies')
		user8 = User.objects.create_user('baddie8', 'baddie8@example.com', 'Teletubies')
		user9 = User.objects.create_user('baddie9', 'baddie9@example.com', 'Teletubies')
		user10 = User.objects.create_user('baddie10', 'baddie10@example.com', 'Teletubies')
		user3.teamprofile.join_team(self.team1)
		user4.teamprofile.join_team(self.team1)
		user5.teamprofile.join_team(self.team1)
		user6.teamprofile.join_team(self.team1)
		user7.teamprofile.join_team(self.team1)
		user8.teamprofile.join_team(self.team1)
		user9.teamprofile.join_team(self.team1)
		user10.teamprofile.join_team(self.team1)
		
		response = self.client.get(reverse('teams_view', args=(self.team1.id,)))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.team1.name)
		self.assertContains(response, self.user1.username)
		self.assertContains(response, 'Team is full.')
		self.assertNotContains(response, reverse('teams_store_request_ids', args=(self.team1.id,)))
	
	def test_exists_team_not_full(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		
		response = self.client.get(reverse('teams_view', args=(self.team1.id,)))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.team1.name)
		self.assertContains(response, self.user1.username)
		self.assertNotContains(response, 'Team is full.')
		self.assertContains(response, reverse('teams_store_request_ids', args=(self.team1.id,)))
	
	def test_exists_team_not_full_but_for_different_user(self):
		self.team1.save()
		self.user2.teamprofile.join_team(self.team1)
		
		response = self.client.get(reverse('teams_view', args=(self.team1.id,)))
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.team1.name)
		self.assertContains(response, self.user2.username)
		self.assertNotContains(response, 'Team is full.')
		self.assertNotContains(response, reverse('teams_store_request_ids', args=(self.team1.id,)))

class ViewMyTeamTestCase(BaseTestCase):
	def test_not_on_team(self):
		response = self.client.get(reverse('teams_view_my_team'), follow=True)
		
		self.assertRedirects(response, reverse('teams_index'))
		self.assertContains(response, NOT_ON_TEAM_MSG())
	
	def test_is_on_team(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		
		response = self.client.get(reverse('teams_view_my_team'))
		
		self.assertRedirects(response, reverse('teams_view', args=[self.team1.id]))

class CreateTestCase(BaseTestCase):
	def test_get(self):
		response = self.client.get(reverse('teams_create'))
		
		self.assertEqual(response.status_code, 200)
	
	def test_post_success(self):
		post_data = {
			'name': 'foo bar',
		}
		
		self.assertEqual(Team.objects.count(), 0)
		
		response = self.client.post(reverse('teams_create'), post_data)
		
		teams = Team.objects.all()
		
		self.assertEqual(len(teams), 1)
		self.assertRedirects(response, reverse('teams_view', args=(teams[0].id,)))
	
	def test_post_fail(self):
		self.team1.save()
		post_data = {
			'name': self.team1.name,
		}
		
		self.assertEqual(Team.objects.count(), 1)
		
		response = self.client.post(reverse('teams_create'), post_data)
		
		teams = Team.objects.all()
		
		self.assertEqual(len(teams), 1)
		self.assertEqual(response.status_code, 200)
		
		self.assertFormError(response, 'form', 'name', 'Team with this Name already exists.')

class BecomeLeaderTestCase(BaseTestCase):
	def test_post_success(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		
		self.assertEqual(self.user1.teamprofile.team, self.team1)
		self.assertEqual(self.user1.teamprofile.leader, False)
		
		response = self.client.post(reverse('teams_become_leader'))
		
		self.assertRedirects(response, reverse('teams_view', args=(self.team1.id,)))
		self.assertEqual(TeamProfile.objects.get(user=self.user1).leader, True)
	
	def test_post_fail_no_team(self):
		self.team1.save()
		
		self.assertEqual(self.user1.teamprofile.team, None)
		self.assertEqual(self.user1.teamprofile.leader, False)
		
		response = self.client.post(reverse('teams_become_leader'), follow=True)
		
		self.assertRedirects(response, reverse('teams_index'))
		self.assertEqual(TeamProfile.objects.get(user=self.user1).leader, False)
		self.assertContains(response, str(NotOnATeamError(self.user1)))
	
	def test_post_fail_already_has_leader(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		self.user2.teamprofile.join_team(self.team1)
		self.user2.teamprofile.become_leader()
		
		self.assertEqual(self.user1.teamprofile.team, self.team1)
		self.assertEqual(self.user1.teamprofile.leader, False)
		
		response = self.client.post(reverse('teams_become_leader'), follow=True)
		
		self.assertRedirects(response, reverse('teams_view', args=(self.team1.id,)))
		self.assertEqual(TeamProfile.objects.get(user=self.user1).leader, False)
		self.assertContains(response, TeamAlreadyHasALeaderError.msg)
	
	def test_get_and_has_no_team(self):
		self.team1.save()
		
		self.assertEqual(self.user1.teamprofile.team, None)
		self.assertEqual(self.user1.teamprofile.leader, False)
		
		response = self.client.get(reverse('teams_become_leader'))
		
		self.assertRedirects(response, reverse('teams_index'))
		self.assertEqual(TeamProfile.objects.get(user=self.user1).leader, False)
	
	def test_get_and_has_team(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		
		self.assertEqual(self.user1.teamprofile.team, self.team1)
		self.assertEqual(self.user1.teamprofile.leader, False)
		
		response = self.client.get(reverse('teams_become_leader'))
		
		self.assertRedirects(response, reverse('teams_view', args=(self.team1.id,)))
		self.assertEqual(TeamProfile.objects.get(user=self.user1).leader, False)

class KickOutTestCase(BaseTestCase):
	def test_kick_out_post_success(self):
		self.team1.save()
		p1 = self.user1.teamprofile
		p1.join_team(self.team1)
		p1.become_leader()
		p2 = self.user2.teamprofile
		p2.join_team(self.team1)
		
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, True)
		self.assertEqual(p2.team, self.team1)
		self.assertEqual(p2.leader, False)
		
		response = self.client.post(reverse('teams_kick_out', args=(self.user2.id,)))
		
		self.assertRedirects(response, reverse('teams_view', args=(self.team1.id,)))
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, True)
		self.assertEqual(p2.team, None)
		self.assertEqual(p2.leader, False)
	
	def test_kick_out_post_fail_user1_not_on_team(self):
		self.team1.save()
		p1 = self.user1.teamprofile
		p2 = self.user2.teamprofile
		p2.join_team(self.team1)
		
		self.assertEqual(p1.team, None)
		self.assertEqual(p1.leader, False)
		self.assertEqual(p2.team, self.team1)
		self.assertEqual(p2.leader, False)
		
		response = self.client.post(reverse('teams_kick_out', args=(self.user2.id,)), follow=True)
		
		self.assertRedirects(response, reverse('teams_index'))
		self.assertContains(response, NotOnATeamError(self.user1))
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, None)
		self.assertEqual(p1.leader, False)
		self.assertEqual(p2.team, self.team1)
		self.assertEqual(p2.leader, False)
	
	def test_kick_out_post_fail_user1_not_a_leader(self):
		self.team1.save()
		p1 = self.user1.teamprofile
		p1.join_team(self.team1)
		p2 = self.user2.teamprofile
		p2.join_team(self.team1)
		
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, False)
		self.assertEqual(p2.team, self.team1)
		self.assertEqual(p2.leader, False)
		
		response = self.client.post(reverse('teams_kick_out', args=(self.user2.id,)), follow=True)
		
		self.assertRedirects(response, reverse('teams_view', args=(self.team1.id,)))
		self.assertContains(response, NotALeaderError())
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, False)
		self.assertEqual(p2.team, self.team1)
		self.assertEqual(p2.leader, False)
	
	def test_kick_out_post_fail_user2_not_on_team(self):
		self.team1.save()
		p1 = self.user1.teamprofile
		p1.join_team(self.team1)
		p1.become_leader()
		p2 = self.user2.teamprofile
		
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, True)
		self.assertEqual(p2.team, None)
		self.assertEqual(p2.leader, False)
		
		response = self.client.post(reverse('teams_kick_out', args=(self.user2.id,)), follow=True)
		
		self.assertRedirects(response, reverse('teams_view', args=(self.team1.id,)))
		self.assertContains(response, NotOnATeamError(self.user2))
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, True)
		self.assertEqual(p2.team, None)
		self.assertEqual(p2.leader, False)
	
	def test_kick_out_post_fail_not_on_same_team(self):
		self.team1.save()
		self.team2.save()
		p1 = self.user1.teamprofile
		p1.join_team(self.team1)
		p1.become_leader()
		p2 = self.user2.teamprofile
		p2.join_team(self.team2)
		
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, True)
		self.assertEqual(p2.team, self.team2)
		self.assertEqual(p2.leader, False)
		
		response = self.client.post(reverse('teams_kick_out', args=(self.user2.id,)), follow=True)
		
		self.assertRedirects(response, reverse('teams_view', args=(self.team1.id,)))
		self.assertContains(response, NotOnSameTeamError())
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, True)
		self.assertEqual(p2.team, self.team2)
		self.assertEqual(p2.leader, False)
	
	def test_get(self):
		self.team1.save()
		p1 = self.user1.teamprofile
		p2 = self.user2.teamprofile
		p1.join_team(self.team1)
		p2.join_team(self.team1)
		
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p2.team, self.team1)
		
		response = self.client.get(reverse('teams_kick_out', args=(self.user2.id,)))
		
		self.assertRedirects(response, reverse('teams_view', args=(self.team1.id,)))
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p2.team, self.team1)

class LeaveTestCase(BaseTestCase):
	def test_post(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		
		self.assertEqual(self.user1.teamprofile.team, self.team1)
		
		response = self.client.post(reverse('teams_leave'))
		
		self.assertRedirects(response, reverse('teams_index'))
		self.assertEqual(TeamProfile.objects.get(user=self.user1).team, None)
	
	def test_get(self):
		self.team1.save()
		self.user1.teamprofile.join_team(self.team1)
		
		self.assertEqual(self.user1.teamprofile.team, self.team1)
		
		response = self.client.get(reverse('teams_leave'))
		
		self.assertRedirects(response, reverse('teams_view', args=(self.team1.id,)))
		self.assertEqual(TeamProfile.objects.get(user=self.user1).team, self.team1)

class StoreRequestIdsTestCase(BaseTestCase):
	def test_storage_successful(self):
		self.team1.save()
		self.assertEqual(self.user1.facebookrequest_set.get_by_type(TeamFacebookRequest).count(), 0)
		
		request_id = '123456'
		
		response = self.client.post(
			reverse('teams_store_request_ids', args=(self.team1.id,)),
			data='["%s"]' % request_id,
			content_type='text/json'
		)
		
		self.assertEqual(response.status_code, 200)
		requests = self.user1.facebookrequest_set.get_by_type(TeamFacebookRequest).all()
		self.assertEqual(len(requests), 1)
		self.assertEqual(requests[0].id, request_id)
		

