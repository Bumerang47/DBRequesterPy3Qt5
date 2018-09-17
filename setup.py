#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='db_requester',
    version='0.1.0',
    description='simple of test application for running SQL requestings on some DBMS',
    author='Ulyantsev Aleksandr',
    author_email='it.bumerang@gmail.com',
    url='https://github.com/Bumerang47/DBRequesterPy3Qt5',
    license='GPL-2',
    long_description=open('README.md').read(),
    install_requires=open('requirements.txt').read().splitlines(),
    extras_require={
      'dev':  [
          'flake8'
      ]
    },
    entry_points={
        'console_scripts': [
            'db_requester=db_requester.main:run_application'
        ]
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.ui', 'icons/*.png'],
    },
    zip_safe=False,
)
