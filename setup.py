#!/usr/bin/env python3
# encoding=utf-8

import os

from appyratus.util.setup import RealSetup

setup = RealSetup(
    path=os.path.abspath(os.path.dirname(__file__)),
    name='appyratus',
    version='0',
    description="Not yo momma's python tool",
    author='Gigaquads',
    author_email='notdsk@gmail.com',
    url='https://github.com/gigaquads/appyratus.git',
    classifiers=['python3', 'mit-license'],
)
setup.run()
