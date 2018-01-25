#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='order_profit',
    version='1.0',
    description='Find profit and loss for Cloud Commerce orders.',
    author='Luke Shiner',
    install_requires=['tabler'],
    packages=find_packages(),
    include_package_data=True,
    )
