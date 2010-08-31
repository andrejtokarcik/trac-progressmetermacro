#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name = 'TracProgressMeterMacro',
    version = '0.2',
    packages = ['progressmeter'],
    package_data = {'progressmeter': ['templates/*.html']},

    author = 'Andrej "qwp0" T',
    author_email = 'androsis@gmail.com',
    description = '''Progress meter macro plugin for Trac''',
    url = 'http://trac-hacks.org/wiki/ProgressMeterMacro',
    license = 'BSD',

    install_requires = ['Trac >= 0.11.5'],
    classifiers = [
        'Framework :: Trac',
    ],

    entry_points = '''
        [trac.plugins]
        progressmeter.macro = progressmeter.macro
    '''
)
