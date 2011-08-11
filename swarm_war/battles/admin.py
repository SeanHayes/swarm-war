# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Python imports
import logging

#Django imports
from django.contrib import admin

#App imports
from models import BattleRecord

logger = logging.getLogger(__name__)

admin.site.register(BattleRecord)
