#!/bin/bash

# clean package build
rm -rf debian

# generate pythonic debian rules
python3 setup.py --command-packages=stdeb.command debianize

# set compatiblity level that automatically hooks up systemd services
echo 10 > debian/compat

# copy automatically enabled/started service to debian folder
cp *.service debian

# add --with systemd to debhelper command
sed -i -e 's/--with python3/--with python3 --with systemd/g' debian/rules

# add service to installinit
echo "override_dh_installinit:" >> debian/rules
echo -e "\tdh_installinit --name=networkd-state" >> debian/rules

# define py3dist overrides, which translates install_requires to debian package dependencies
echo "gi python3-gi" >> debian/py3dist-overrides
echo "dbus python3-dbus" >> debian/py3dist-overrides

# build package
fakeroot debian/rules binary
