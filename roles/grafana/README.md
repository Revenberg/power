
curl http://localhost/api/alert-notifications -u admin:admin


influx -execute 'SELECT * FROM "p1" ' -database="power" -precision=rfc3339
influx -execute 'SELECT * FROM "solar" ' -database="power" -precision=rfc3339
influx -execute 'SELECT * FROM "weather" ' -database="power" -precision=rfc3339

sudo du -a /var | sort -n -r | head -n 20


influx -execute 'SELECT mean("+P"),mean("+P1"),mean("+P2"),mean("+P3"),mean("+T"),mean("+T1"),mean("+T2"),mean("-P"),mean("-P1"),mean("-P2"),mean("-P3"),mean("-T"),mean("-T1"),mean("-T2"),mean("G"),mean("P") FROM "p1" GROUP BY time(5m)' -database="power" -precision=rfc3339 | head


