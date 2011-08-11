# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib import admin

#App imports
from models import Collection, CollectionItem

class CollectionItemAdmin(admin.TabularInline):
	model = CollectionItem
	fk_name = 'collection'
	extra = 1

class CollectionAdmin(admin.ModelAdmin):
	inlines = [CollectionItemAdmin]

admin.site.register(Collection, CollectionAdmin)
admin.site.register(CollectionItem)

