#!/bin/bash
rm -rf debian
python3 setup.py --command-packages=stdeb.command debianize
echo 10 > debian/compat
cp *.service debian
cp *.target debian

# add --with systemd to debhelper command
sed -i -e 's/--with python3/--with python3 --with systemd/g' debian/rules

# add service to installinit
echo "override_dh_installinit:" >> debian/rules
echo -e "\tdh_installinit --name=networkd-state" >> debian/rules

echo "gi python3-gi" >> debian/py3dist-overrides
echo "dbus python3-dbus" >> debian/py3dist-overrides

fakeroot debian/rules binary
