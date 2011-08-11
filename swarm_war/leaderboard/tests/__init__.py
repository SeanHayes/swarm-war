# -*- coding: utf-8 -*-
#Copyright (C) 2011 Seán Hayes

#Django imports
from django.test import TestCase

#App imports
from test_managers import *
from test_models import *
from test_urls import *

__test__ = {
	'test_managers': [test_managers],
	'test_models': [test_models],
	'test_urls': [test_urls],
}

