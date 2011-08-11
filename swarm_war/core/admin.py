# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib import admin

#App imports
from models import Item, UserItem, CoreProfile, FacebookRequest

#TODO: only edit Items that aren't a subtype?
class ItemAdmin(admin.ModelAdmin):
	readonly_fields = ['id']

admin.site.register(Item, ItemAdmin)
admin.site.register(UserItem)

class CoreProfileAdmin(admin.ModelAdmin):
	exclude = ['allies']
	readonly_fields = ['get_experience_level']
admin.site.register(CoreProfile, CoreProfileAdmin)

admin.site.register(FacebookRequest)
