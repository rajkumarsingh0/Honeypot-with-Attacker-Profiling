#!/bin/bash
# install_cowrie.sh
#
# Documents the steps used to install Cowrie (official project,
# https://github.com/cowrie/cowrie) as a dedicated, non-root user.
# Run these manually / adapt as needed -- this is a reference script,
# not meant to be run unattended.

set -e

echo "== 1. Create a dedicated non-root 'cowrie' user =="
sudo adduser --disabled-password --gecos "" cowrie
echo "(then: su - cowrie, and run the rest as that user)"

echo "== 2. Clone and install Cowrie into a venv =="
git clone https://github.com/cowrie/cowrie.git
cd cowrie
python3 -m venv cowrie-env
source cowrie-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .          # installs the 'cowrie' console command
pip install mysql-connector-python   # required by output_mysql plugin

echo "== 3. Configure Cowrie =="
cp src/cowrie/data/etc/cowrie.cfg.dist etc/cowrie.cfg
cp src/cowrie/data/etc/userdb.example etc/userdb.txt
echo "Now manually apply the settings in ../cowrie-config/cowrie.cfg.custom"
echo "to etc/cowrie.cfg (ssh listen port, hostname, output_mysql block)."

echo "== 4. Import Cowrie's own MySQL schema (run as a sudo-capable user) =="
echo "sudo mysql cowrie < docs/sql/mysql.sql"
echo "(Cowrie's update*.sql scripts are NOT needed on recent versions --"
echo " mysql.sql already contains the full current schema.)"

echo "== 5. Start Cowrie =="
echo "cowrie start"
echo "cowrie status"
