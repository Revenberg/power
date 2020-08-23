
curl http://localhost/api/alert-notifications -u admin:admin


influx -execute 'SELECT * FROM "p1" ' -database="power" -precision=rfc3339
influx -execute 'SELECT * FROM "solar" ' -database="power" -precision=rfc3339
influx -execute 'SELECT * FROM "weather" ' -database="power" -precision=rfc3339