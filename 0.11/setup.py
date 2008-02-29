#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name = 'TracProgressMeterMacro',
    version = '0.1',
    packages = ['progressmeter'],
    package_data = { 'progressmeter': ['htdocs/css/*.css'] },

    author = 'Andrej "qwp0" Tokarčík',
    author_email = 'androsis@gmail.com',
    description = '''Plugin for Trac (http://trac.edgewall.org)
                     which provides ProgressMeter wiki macro''',
    url = 'http://trac-hacks.org/wiki/ProgressMeterMacro',
    license = 'GPL',

    install_requires = ['Trac'],
    classifiers = [
        'Framework :: Trac',
    ],

    entry_points = ''' 
        [trac.plugins]
        progressmeter.macro = progressmeter.macro
    '''
)
