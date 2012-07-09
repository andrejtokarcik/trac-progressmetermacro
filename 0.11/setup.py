#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name = 'TracProgressMeterMacro',
    version = '0.4',
    packages = find_packages(exclude=['*.tests*']),
    package_data = {'progressmeter': ['templates/*.html']},

    author = 'Andrej Tokarčík',
    author_email = 'andrejtokarcik@gmail.com',
    description = '''Progress meter macro plugin for Trac''',
    url = 'http://trac-hacks.org/wiki/ProgressMeterMacro',
    license = 'BSD',

    install_requires = ['Python >= 2.5', 'Trac >= 0.11.5'],
    classifiers = [
        'Framework :: Trac',
    ],

    entry_points = '''
        [trac.plugins]
        progressmeter.macro = progressmeter.macro
    '''
)
