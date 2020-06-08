#!/usr/bin/python3
"""
Create systemd targets for interface state updates

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
import argparse
import os


def main():
    """
    Main tool to create state targets
    """
    parser = argparse.ArgumentParser(
        description='Create networkd-state target for an interface')
    parser.add_argument(
        'interface', help='interface to manage')
    parser.add_argument(
        '-s', '--state', help='target state that should trigger a notification', default='routable')
    args = parser.parse_args()

    target = f'/lib/systemd/system/networkd-state@.target'
    link_name = f'/etc/systemd/system/networkd-state@{args.interface}-{args.state}.target'
    os.symlink(target, link_name)


if __name__ == '__main__':
    main()
