#!/bin/bash
sudo apt-get update 
sudo apt-get autoremove

sudo apt-get install git -y 

# Install Ansible and Git on the machine.
sudo apt-get install python-pip git python-dev sshpass -y
sudo pip install ansible 
sudo pip install markupsafe 

rm -rf /home/pi/power
git clone https://github.com/Revenberg/power.git 

# ansible-playbook /home/pi/power/setup.yml
#ansible-playbook /home/pi/power/grafana.yml --ask-vault-pass
ansible-playbook /home/pi/power/grafana.1.yml --vault-password-file /home/pi/pswrd