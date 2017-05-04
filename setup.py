#-*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Flask-Mysqlpool
-----------
Adds support to flask to connect to a MySQL server using
mysqldb extension and a connection pool.
"""

from setuptools import setup

setup(
    name='Flask-Mysqlpool',
    version='0.1',
    url='',
    license='BSD',
    author='Giorgos Komninos',
    author_email='g+ext@gkomninos.com',
    description='Flask simple mysql client using a connection pool',
    long_description=__doc__,
    packages=[
        'flask_mysqlpool',
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'mysql-python',
    ],
    test_suite='test_mysqlpool',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

