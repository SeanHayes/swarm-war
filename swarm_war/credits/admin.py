# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.contrib import admin

#App imports
from models import Listing, PurchaseRecord

admin.site.register(Listing)

class PurchaseRecordAdmin(admin.ModelAdmin):
	readonly_fields = [
		'receiver',
		'listings',
		'datetime',
	]
admin.site.register(PurchaseRecord, PurchaseRecordAdmin)
