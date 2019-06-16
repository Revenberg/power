#!/bin/bash
sudo apt-get update 
sudo apt-get autoremove

sudo apt-get install git -y 

# Install Ansible and Git on the machine.
sudo apt-get install python-pip git python-dev sshpass -y
sudo pip install ansible 
sudo pip install markupsafe 

git clone https://github.com/Revenberg/power.git 

cd /home/pi/power
ansible-playbook setup.yml
cd ansible-playbook graphana.yml