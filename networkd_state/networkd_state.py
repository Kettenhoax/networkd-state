#!/usr/bin/python3
"""
Subscribe to dbus events for network interface changes, and start/stop
systemd targets accordingly

Copyright 2020 Marcel Zeilinger <marcel.zeilinger@live.at>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import logging
import argparse
import subprocess
import sys
import os
from shutil import which
from typing import NamedTuple

from gi.repository import GLib as glib

import dbus
import dbus.mainloop.glib

DBUS_NETWORKD_LINK_PREFIX = '/org/freedesktop/network1/link/_'


class InterfaceData(NamedTuple):
    """
    Struct for network interface data
    """
    name: str
    state: str


def resolve_path(paths):
    """
    Resolve path of a file from multiple options
    """
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def get_interface_index(object_path):
    """
    Parses the index of the network interface from DBus network path

    Parameters

    `object_path` is the path to the networkd interface object on the DBus
    """
    # https://lists.freedesktop.org/archives/systemd-devel/2016-May/036525.html
    # object path ends in '_' concatenated with the ascii ordinal as string
    idx = object_path[len(DBUS_NETWORKD_LINK_PREFIX):]
    return int(chr(int(idx[:2], 16)))


class InterfaceStatusManager:
    """
    Maintains a cache of network interface status and starts systemd targets for when their new
    state is the target state
    """

    def __init__(self, ifaces, state):
        """
        Create manager with list of network interfaces and state on which to active targets
        """
        self._managed_ifaces = ifaces
        self._target_state = state

        # listen on system-wide bus for networkd events
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self._bus = dbus.SystemBus()
        self._systemd1 = self._bus.get_object(
            'org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        self._manager = dbus.Interface(
            self._systemd1, 'org.freedesktop.systemd1.Manager')
        # map of interface indices to their data
        self._ifaces = {}

    def run(self):
        """
        Run manager indefinitely

        Will block the process
        """
        self._bus.add_signal_receiver(self._property_changed,
                                      bus_name='org.freedesktop.network1',
                                      signal_name='PropertiesChanged',
                                      path_keyword='path')

        # initialize the initial interface map
        self._update_iface_map()
        for idx in self._ifaces:
            data = self._ifaces[idx]
            self._update_target(data.name, data.state == self._target_state)

        # main loop
        mainloop = glib.MainLoop()
        mainloop.run()

    def _update_iface_map(self):
        """
        Query state of interfaces and update `IFACE_MAP`
        """
        out = subprocess.check_output(
            ['networkctl', 'list', '--no-pager', '--no-legend'])
        self._ifaces.clear()
        for line in out.split(b'\n')[:-1]:
            fields = line.decode('ascii').split()
            idx = int(fields[0])
            name = fields[1]
            if name not in self._managed_ifaces:
                continue
            state = fields[3]
            data = InterfaceData(name, state)
            self._ifaces[idx] = data

    def _property_changed(self, typ, data, _, path):
        """
        Networkd notification callback
        """
        if typ != 'org.freedesktop.network1.Link':
            return
        if not path.startswith(DBUS_NETWORKD_LINK_PREFIX):
            return
        if data.get('AdministrativeState') == 'initialized':
            self._update_iface_map()
        if 'OperationalState' not in data:
            return
        state = data['OperationalState']

        idx = get_interface_index(path)
        name = self._ifaces[idx].name
        if name not in self._managed_ifaces:
            return

        new_data = InterfaceData(name, state)
        self._ifaces[idx] = new_data
        self._update_target(name, state == self._target_state)

    def _update_target(self, iface_name, state):
        """
        `state` is False or True, to set the target accordingly
        """
        if state:
            state_name = 'enabled'
        else:
            state_name = 'disabled'
        unit = f'{iface_name}-{self._target_state}.target'
        logging.debug('Set %s to %s', unit, state_name)
        if state:
            self._manager.StartUnit(unit, 'fail')
        else:
            self._manager.StopUnit(unit, 'fail')


def main():
    """
    Subscribe to networkd notifications and run indefinitely
    """
    parser = argparse.ArgumentParser(
        description='networkd interface state daemon')
    parser.add_argument(
        '-i', '--iface', nargs='+', help='interfaces to manage')
    parser.add_argument(
        '--verbose', action='store_true', help='verbose output')
    parser.add_argument(
        '-s', '--state', help='target state that should trigger a notification', default='routable')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if which('networkctl') is None:
        sys.exit("networkctl binary not found")

    mgr = InterfaceStatusManager(args.iface, args.state)
    mgr.run()


if __name__ == '__main__':
    main()
