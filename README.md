# networkd-state: systemd targets for network interface states

## Deprecation

While I keep this project as an example how to use DBus to react to networkd events, I recommend to use the networkd-online service specifically to wait for routable networks.

To wait for specific network links only, run `systemctl edit systemd-networkd-wait-online.service` and overwrite the interfaces it waits for, in this case eth0.
Then you can depend on systemd-networkd-wait-online in your other units using `After=` directives.

```
[Service]
ExecStart=
ExecStart=/lib/systemd/systemd-networkd-wait-online -i eth0
```

## Summary

`networkd-state` starts and stops systemd target units in reaction to network interface state changes.

This is useful to start/stop applications for hot-pluggable ethernet devices connected to computers with multiple network interfaces, e.g. GigE vision cameras.

## Usage

Install the manager service.

```bash
sudo python3 setup.py install
```

Create a systemd target `networkd-state@${INTERFACE_NAME}-${STATE}.target` in `/etc/systemd/system`, e.g. `networkd-state@eth0-routable.target`, either manually or using this shortcut:

```bash
# implicitly uses routable as target state
networkd-state-create-target eth0
# alternatively, to create a target for every interface, run
# networkd-state-create-target
```

If you want to restrict updates to a subset of interfaces, direct networkd-state to do so in a command override:

```bash
systemctl edit networkd-state
```

```ini
# restricts state updates to interface eth0
[Service]
ExecStart=
ExecStart=/usr/lib/networkd_state/networkd_state -i eth0
```

To deploy as package, create a deb file.

```bash
./create_deb.bash
# install the resulting ../*.deb files on the target machine
```

## Dependencies

`networkd-state` depends on:

- Python 3.6+
- PyGObject/PyGI (``python3-gi``)
- Python D-Bus (``python3-dbus``)

## Authors and Copyright

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