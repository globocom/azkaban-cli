'''
Created on 2018-03-22

@author: gustavo.alves
'''
from setuptools import setup, find_packages

version = u'0.4.1'

setup(
    name='azkaban_cli',
    version=version,
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
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        'requests==2.18.4',
        'click==6.7',
    ],
    entry_points='''
        [console_scripts]
        azkaban=azkaban_cli.azkaban_cli:cli
    ''',
)
