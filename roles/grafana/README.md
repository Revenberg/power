
curl http://localhost/api/alert-notifications -u admin:admin


influx -execute 'SELECT * FROM "p1" ' -database="power" -precision=rfc3339
influx -execute 'SELECT * FROM "solar" ' -database="power" -precision=rfc3339
influx -execute 'SELECT * FROM "weather" ' -database="power" -precision=rfc3339

sudo du -a /var | sort -n -r | head -n 20


influx -execute 'SELECT * FROM "p1_mean" ' -database="power" -precision=rfc3339 |head -n 10