# https://engineer.john-whittington.co.uk/2016/11/raspberry-pi-data-logger-influxdb-grafana/
# update these URLs by looking at the website: https://packages.debian.org/sid/grafana
# https://grafana.com/grafana/plugins/fetzerch-sunandmoon-datasource/installation
# https://grafana.com/grafana/plugins/fetzerch-sunandmoon-datasource/installation
# influx -execute 'SELECT * FROM "PV" LIMIT 3' -database="telemetry" -precision=rfc3339

sudo apt-get update -y
sudo apt-get upgrade -y
wget http://ftp.us.debian.org/debian/pool/main/i/influxdb/influxdb_1.0.2+dfsg1-1_armhf.deb
sudo dpkg -i influxdb_1.0.2+dfsg1-1_armhf.deb
wget http://ftp.us.debian.org/debian/pool/main/g/grafana/grafana-data_2.6.0+dfsg-3_all.deb # grafana data is a dependancy for grafana
sudo dpkg -i grafana-data_2.6.0+dfsg-3_all.deb
sudo apt-get install -f -y
wget http://ftp.us.debian.org/debian/pool/main/g/grafana/grafana_2.6.0+dfsg-3_armhf.deb
sudo dpkg -i grafana_2.6.0+dfsg-3_armhf.deb
sudo apt-get install -f -y
sudo pip install influxdb

sudo python -m pip install automationhat
sudo apt install python-smbus -y
