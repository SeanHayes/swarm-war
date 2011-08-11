# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib import admin

#App imports
from models import *

admin.site.register(Area)

class MissionItemAdmin(admin.TabularInline):
	model = MissionItem
	fk_name = 'mission'
	extra = 1

class MissionTriggerAdmin(admin.TabularInline):
	model = MissionTrigger
	fk_name = 'mission'
	extra = 1

class MissionAdmin(admin.ModelAdmin):
	inlines = [MissionTriggerAdmin, MissionItemAdmin]

admin.site.register(Mission, MissionAdmin)

admin.site.register(MissionItem)

admin.site.register(MissionTrigger)

admin.site.register(UserMission)

admin.site.register(MissionProfile)
