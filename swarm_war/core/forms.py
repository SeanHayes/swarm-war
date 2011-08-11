# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django import forms
from django.forms.extras.widgets import Select

class BuyItemForm(forms.Form):
	quantity = forms.IntegerField(min_value=1)#, choices=xrange(1, 11), widget=Select)

class SellItemForm(forms.Form):
	quantity = forms.IntegerField(min_value=1)#, choices=xrange(1, 11), widget=Select)

class RefillForm(forms.Form):
	#TODO: make it a choice field that takes values from CoreProfile.REFILL_DATA
	attr = forms.CharField(max_length=50)
