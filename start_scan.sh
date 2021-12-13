#!/bin/bash

BASEDIR=<PATH TO APPDIR>
cd $BASEDIR
source venv/bin/activate
python3 -m ssh_keyscanner -c config.yaml -f test_hosts.txt
