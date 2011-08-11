# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import pdb

#Django imports
from django.contrib.auth.models import User

#App imports
from ..exceptions import TeamAlreadyExistsError, TeamFullError, NotOnATeamError, TeamAlreadyHasALeaderError, NotOnSameTeamError, NotALeaderError
from ..models import Team, TeamProfile
from util import BaseTestCase

class TeamTestCase(BaseTestCase):
	#get_leader
	
	def test_get_leader_returns_user(self):
		team_name = 'Foo Bar'
		p = self.user1.teamprofile
		p.create_team(team_name)
		team = Team.objects.all()[0]
		
		self.assertEqual(team.get_leader(), self.user1)
	
	def test_get_leader_returns_none(self):
		team_name = 'Foo Bar'
		p = self.user1.teamprofile
		p.create_team(team_name)
		p.leader = False
		p.save()
		team = Team.objects.all()[0]
		
		self.assertEqual(team.get_leader(), None)

class TeamProfileTestCase(BaseTestCase):
	#become_leader
	
	def test_become_leader_success(self):
		self.team1.save()
		p = self.user1.teamprofile
		p.join_team(self.team1)
		
		self.assertEqual(p.team, self.team1)
		self.assertEqual(p.leader, False)
		
		p.become_leader()
		
		p = TeamProfile.objects.get(user=self.user1)
		self.assertEqual(p.leader, True)
	
	def test_become_leader_fail_not_on_team(self):
		p = self.user1.teamprofile
		
		self.assertEqual(p.team, None)
		self.assertEqual(p.leader, False)
		
		self.assertRaises(NotOnATeamError, p.become_leader)
		
		p = TeamProfile.objects.get(user=self.user1)
		self.assertEqual(p.leader, False)
	
	def test_become_leader_fail_already_has_leader(self):
		self.team1.save()
		p1 = self.user1.teamprofile
		p1.join_team(self.team1)
		p2 = self.user2.teamprofile
		p2.join_team(self.team1)
		p2.become_leader()
		
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, False)
		self.assertEqual(p2.team, self.team1)
		self.assertEqual(p2.leader, True)
		
		self.assertRaises(TeamAlreadyHasALeaderError, p1.become_leader)
		
		p1 = TeamProfile.objects.get(user=self.user1)
		self.assertEqual(p1.leader, False)
	
	#create_team
	
	def test_create_team_success(self):
		team_name = 'Foo Bar'
		p = self.user1.teamprofile
		
		self.assertEqual(p.team, None)
		self.assertEqual(p.leader, False)
		self.assertEqual(Team.objects.count(), 0)
		
		p.create_team(team_name)
		
		team = Team.objects.all()[0]
		
		p = TeamProfile.objects.get(user=self.user1)
		self.assertEqual(p.team, team)
		self.assertEqual(p.leader, True)
		self.assertEqual(Team.objects.count(), 1)
	
	def test_create_team_fail(self):
		self.team1.save()
		p = self.user1.teamprofile
		
		self.assertEqual(p.team, None)
		self.assertEqual(p.leader, False)
		self.assertEqual(Team.objects.count(), 1)
		
		self.assertRaises(TeamAlreadyExistsError, p.create_team, *(self.team1.name,))
		
		p = TeamProfile.objects.get(user=self.user1)
		self.assertEqual(p.team, None)
		self.assertEqual(p.leader, False)
		self.assertEqual(Team.objects.count(), 1)
	
	#join_team
	
	def test_join_team_success(self):
		self.team1.save()
		p = self.user1.teamprofile
		
		self.assertEqual(p.team, None)
		self.assertEqual(p.leader, False)
		self.assertEqual(Team.objects.count(), 1)
		
		p.join_team(self.team1)
		
		p = TeamProfile.objects.get(user=self.user1)
		self.assertEqual(p.team, self.team1)
		self.assertEqual(p.leader, False)
		self.assertEqual(Team.objects.count(), 1)
	
	def test_join_team_team_is_full(self):
		self.team1.save()
		user3 = User.objects.create_user('baddie3', 'baddie3@example.com', 'Teletubies')
		user4 = User.objects.create_user('baddie4', 'baddie4@example.com', 'Teletubies')
		user5 = User.objects.create_user('baddie5', 'baddie5@example.com', 'Teletubies')
		user6 = User.objects.create_user('baddie6', 'baddie6@example.com', 'Teletubies')
		user7 = User.objects.create_user('baddie7', 'baddie7@example.com', 'Teletubies')
		user8 = User.objects.create_user('baddie8', 'baddie8@example.com', 'Teletubies')
		user9 = User.objects.create_user('baddie9', 'baddie9@example.com', 'Teletubies')
		user10 = User.objects.create_user('baddie10', 'baddie10@example.com', 'Teletubies')
		user11 = User.objects.create_user('baddie11', 'baddie11@example.com', 'Teletubies')
		self.user2.teamprofile.join_team(self.team1)
		user3.teamprofile.join_team(self.team1)
		user4.teamprofile.join_team(self.team1)
		user5.teamprofile.join_team(self.team1)
		user6.teamprofile.join_team(self.team1)
		user7.teamprofile.join_team(self.team1)
		user8.teamprofile.join_team(self.team1)
		user9.teamprofile.join_team(self.team1)
		user10.teamprofile.join_team(self.team1)
		user11.teamprofile.join_team(self.team1)
		
		p = self.user1.teamprofile
		
		self.assertEqual(p.team, None)
		self.assertEqual(p.leader, False)
		
		self.assertRaises(TeamFullError, p.join_team, *(self.team1,))
		
		p = TeamProfile.objects.get(user=self.user1)
		self.assertEqual(p.team, None)
		self.assertEqual(p.leader, False)
	
	#kick_out
	
	def test_kick_out_success(self):
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
		
		p1.kick_out(p2.user)
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, True)
		self.assertEqual(p2.team, None)
		self.assertEqual(p2.leader, False)
	
	def test_kick_out_fail_user1_not_on_team(self):
		self.team1.save()
		p1 = self.user1.teamprofile
		p2 = self.user2.teamprofile
		p2.join_team(self.team1)
		
		self.assertEqual(p1.team, None)
		self.assertEqual(p1.leader, False)
		self.assertEqual(p2.team, self.team1)
		self.assertEqual(p2.leader, False)
		
		#FIXME: there's no way to tell which user this error is for
		self.assertRaises(NotOnATeamError, p1.kick_out, *(p2.user,))
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, None)
		self.assertEqual(p1.leader, False)
		self.assertEqual(p2.team, self.team1)
		self.assertEqual(p2.leader, False)
	
	def test_kick_out_fail_user1_not_a_leader(self):
		self.team1.save()
		p1 = self.user1.teamprofile
		p1.join_team(self.team1)
		p2 = self.user2.teamprofile
		p2.join_team(self.team1)
		
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, False)
		self.assertEqual(p2.team, self.team1)
		self.assertEqual(p2.leader, False)
		
		self.assertRaises(NotALeaderError, p1.kick_out, *(p2.user,))
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, False)
		self.assertEqual(p2.team, self.team1)
		self.assertEqual(p2.leader, False)
	
	def test_kick_out_fail_user2_not_on_team(self):
		self.team1.save()
		p1 = self.user1.teamprofile
		p1.join_team(self.team1)
		p1.become_leader()
		p2 = self.user2.teamprofile
		
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, True)
		self.assertEqual(p2.team, None)
		self.assertEqual(p2.leader, False)
		
		#FIXME: there's no way to tell which user this error is for
		self.assertRaises(NotOnATeamError, p1.kick_out, *(p2.user,))
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, True)
		self.assertEqual(p2.team, None)
		self.assertEqual(p2.leader, False)
	
	def test_kick_out_fail_not_on_same_team(self):
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
		
		self.assertRaises(NotOnSameTeamError, p1.kick_out, *(p2.user,))
		
		p1 = TeamProfile.objects.get(user=self.user1)
		p2 = TeamProfile.objects.get(user=self.user2)
		self.assertEqual(p1.team, self.team1)
		self.assertEqual(p1.leader, True)
		self.assertEqual(p2.team, self.team2)
		self.assertEqual(p2.leader, False)
	
	#leave_team
	
	def test_leave_team_members_remain(self):
		team_name = 'Foo Bar'
		p = self.user1.teamprofile
		p.create_team(team_name)
		team = Team.objects.all()[0]
		p2 = self.user2.teamprofile
		p2.join_team(team)
		
		self.assertEqual(p.team, team)
		self.assertEqual(p.leader, True)
		self.assertEqual(Team.objects.count(), 1)
		
		p.leave_team()
		
		p = TeamProfile.objects.get(user=self.user1)
		self.assertEqual(p.team, None)
		self.assertEqual(p.leader, False)
		self.assertEqual(Team.objects.count(), 1)
	
	def test_leave_team_no_members_remain(self):
		team_name = 'Foo Bar'
		p = self.user1.teamprofile
		p.create_team(team_name)
		team = Team.objects.all()[0]
		
		self.assertEqual(p.team, team)
		self.assertEqual(p.leader, True)
		self.assertEqual(Team.objects.count(), 1)
		
		p.leave_team()
		
		p = TeamProfile.objects.get(user=self.user1)
		self.assertEqual(p.team, None)
		self.assertEqual(p.leader, False)
		self.assertEqual(Team.objects.count(), 0)
