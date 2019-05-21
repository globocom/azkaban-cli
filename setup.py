# -*- coding: utf-8 -*-

'''
Created on 2018-03-22

@author: gustavo.alves
'''
from setuptools import setup, find_packages
from azkaban_cli.__version__ import __version__

setup(
    name='azkaban_cli',
    version=__version__,
    author = "Gustavo Alves",
    author_email = "gustavo.alves@corp.globo.com",
    description = ("Azkaban CLI"),
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    py_modules=['azkaban_cli'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        'requests<2.30.0',
        'click<8.0',
        'beautifulsoup4<=4.7.1'
    ],
    tests_require = [
        'responses==0.10.5',
    ],
    entry_points='''
        [console_scripts]
        azkaban=azkaban_cli.azkaban_cli:cli
    ''',
)
