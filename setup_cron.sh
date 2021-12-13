#!/bin/bash
BASEDIR=<PATH TO APPDIR>
cd $BASEDIR
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
crontab -l > tmpcronfile
echo "* */4 * * *   ${BASEDIR}start_scan.sh" >> tmpcronfile
crontab tmpcronfile
rm tmpcronfile
