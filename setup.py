#!/usr/bin/env python3
# encoding=utf-8

import os
from setuptools import setup, find_packages

if __name__ == '__main__':
    HERE = os.path.abspath(os.path.dirname(__file__))

    with open(os.path.join(HERE, 'requirements.txt')) as f:
        REQUIREMENTS = [s.strip().replace('-', '_') for s in f.readlines()]

    setup(
        name='appyratus',
        version='0b1',
        description="Not yo momma's python tool",
        author='Gigaquads',
        author_email='notdsk@gmail.com',
        install_requires=REQUIREMENTS,
        url='https://github.com/gigaquads/appyratus.git',
        packages=find_packages()
    #classifiers=['python3', 'mit-license'],
    )
