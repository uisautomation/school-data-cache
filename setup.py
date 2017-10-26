#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(
    name='cache_school_data',
    # When changing this version number, remember to update CHANGELOG.
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Caches School Data',
    long_description=open('README.md').read(),
    url='https://git.csx.cam.ac.uk/i/ucs/automation/cache_school_data',
    author='Automation team, University Information Services, University of Cambridge',
    author_email='automation@uis.cam.ac.uk',
    install_requires=[
        'boto3',
        'zeep',
    ],
    tests_require=['mock'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
