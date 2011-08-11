#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (C) 2011 Seán Hayes

#This file is part of Foobar.

#Foobar is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#Foobar is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup
import swarm_war

package_name = 'swarm_war'
test_package_name = '%s_test_project' % package_name

setup(name='swarm-war',
	version=swarm_war.__version__,
	description=swarm_war.__doc__,
	author='Seán Hayes',
	author_email='sean@seanhayes.name',
	classifiers=[
		"Development Status :: 4 - Beta",
		"Framework :: Django",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU Affero General Public License v3",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.6",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
		"Topic :: Software Development :: Libraries",
		"Topic :: Software Development :: Libraries :: Python Modules"
	],
	keywords='django facebook game engine',
	url='http://seanhayes.name/',
	package_dir={'util': os.path.join(test_package_name, 'apps', 'util')},
	packages=[
		'swarm_war',
		'swarm_war.battles',
		'swarm_war.battles.tests',
		'swarm_war.core',
		'swarm_war.core.tests',
		'swarm_war.credits',
		'swarm_war.credits.tests',
		'swarm_war.leaderboard',
		'swarm_war.leaderboard.tests',
		'swarm_war.missions',
		'swarm_war.missions.tests',
		'swarm_war.teams',
		'swarm_war.teams.tests',
		'swarm_war_test_project',
		'util',
	],
	package_data={'swarm_war': ['*/templates/*/*']},
	install_requires=['Django>=1.3', 'celery', 'django-celery', 'django-pagination'],
	test_suite = '%s.runtests.runtests' % test_package_name,
)

