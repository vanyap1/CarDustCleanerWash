#!/bin/bash

groupadd i2c
chown :i2c /dev/i2c-0
chmod g+rw /dev/i2c-0
usermod -aG i2c vanya
echo 'KERNEL=="i2c-[0-9]*", GROUP="i2c"' >> /etc/udev/rules.d/10-local_i2c_group.rules
sudo usermod -aG dialout vanya
