#!/bin/bash
if [ ! -f "/home/pi/.pswrd" ]; then
    if [ $# -ne 1 ]; then
        echo $0: usage: ./install.sh  password
        exit 0
    fi

    echo $1 > /home/pi/.pswrd

    sudo apt-get update
    sudo apt-get autoremove

    sudo apt-get install git -y

    # Install Ansible and Git on the machine.
    sudo apt-get install python-pip git python-dev sshpass -y
    sudo pip install ansible
    sudo pip install markupsafe

    # Configure IP address in "hosts" file. If you have more than one
    # Raspberry Pi, add more lines and enter details

    mkdir /home/pi/ansible

    git clone https://github.com/Revenberg/power.git 

    ansible-playbook --connection=local /home/pi/power/changepassword.yml
fi

mkdir /home/pi/.ssh 2>/dev/null

sudo ssh-keygen -l -f /etc/ssh/ssh_host_rsa_key
ssh-keygen -l -f /etc/ssh/ssh_host_rsa_key
ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'  | while read line;
do
    ssh-keyscan -H $line >> ~/.ssh/known_hosts
done
sudo ssh-keygen -l -f /etc/ssh/ssh_host_rsa_key

pswrd=$(cat /home/pi/.pswrd)

echo "all:" > /home/pi/ansible/hosts
echo "  vars:" >> /home/pi/ansible/hosts
echo "    ansible_connection: ssh" >> /home/pi/ansible/hosts
echo "    ansible_ssh_user: pi" >> /home/pi/ansible/hosts
ansible-vault encrypt_string --vault-password-file /home/pi/.pswrd $pswrd --name '    ansible_ssh_pass'  >> /home/pi/ansible/hosts
echo "rpi:" >> /home/pi/ansible/hosts
echo "  hosts:" >> /home/pi/ansible/hosts


ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'  | head -n 1 | while read line;
do
  echo "    $line:" >> /home/pi/ansible/hosts
  echo "      ansible_user: pi" >> /home/pi/ansible/hosts
done

#echo /home/pi/ansible/hosts
#ansible-vault encrypt_string --vault-password-file /home/pi/.pswrd '$pswrd' --name ' ansible_ssh_pass'  >> /home/pi/ansible/hosts

cd /home/pi/power
git pull
cd ~

cp /home/pi/power/install.sh /home/pi/power/install.sh
chmod +x ~/install.sh

ansible-playbook  /home/pi/power/grafana.1.yml --vault-password-file /home/pi/.pswrd -i /home/pi/ansible/hosts 
