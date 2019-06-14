#!/bin/bash
sudo apt-get update 
sudo apt-get autoremove

sudo apt-get install git -y 

# Install Ansible and Git on the machine.
sudo apt-get install python-pip git python-dev sshpass -y
sudo pip install ansible 
sudo pip install markupsafe 

git clone https://github.com/Revenberg/ansible.git 

echo "[local]" > /home/pi/ansible/hosts
echo "localhost   ansible_connection=local" >> ~/ansible/hosts

cd ~/ansible
ansible-playbook setup.yml 