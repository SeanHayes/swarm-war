# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

def xp_level_generator():
	i = 1
	while i < 100:#needed a big number to prevent this from possibly going on forever
		yield (10, i*10)
		i += 1

#should be an iterator (a list returned by a function or a generator) which returns a tuple in the form: (number of levels, number of points for each of these levels,)
DW_CORE_XP_LEVEL_ITERATOR = xp_level_generator

#instead of iterating over a list of tuples, use math!
#Either use this option or DW_CORE_XP_LEVEL_ITERATOR
DW_CORE_XP_LEVEL_MATH_FUNC = False
DW_CORE_ALLIANCE_INVITE_TEXT = "You should check out this awesome game."
DW_CORE_TICK_COUNTDOWN_TASK_NAMES = ['energy_tick', 'stamina_tick', 'health_tick']

DW_CORE_ENERGY_PER_TICK = 5
DW_CORE_HEALTH_PER_TICK = 5
DW_CORE_STAMINA_PER_TICK = 5

#http://developers.facebook.com/docs/reference/api/user/
DW_CORE_FB_POST_DICT = {
	'profile_created': {
		'message': 'This is the message.',
		'link': '/',
		#'picture': 'This is the picture.',
		#'name': 'This is the name.',
		#'caption': 'This is the caption.',
		#'description': 'This is the description.',
		#'actions': [],
		#'privacy': 'privacy',
	},
}
