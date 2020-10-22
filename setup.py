#!/usr/bin/python3
from setuptools import setup
setup(
    data_files=[
        ('lib/networkd_state', ['bin/networkd_state']),
        ('/lib/systemd/system', ['networkd-state@.target']),
    ],
)
