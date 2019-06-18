#!/bin/bash

#curl http://admin:admin@localhost:3000/api/org {"id":1,"name":"Main Org."}

response=$(curl 'http://localhost:3000/api/auth/keys' -XPOST -uadmin:admin -H 'Content-Type: application/json' -d '{"role":"Admin","name":"install_api_key"}' )
api_key=$(echo $response | sed 's/.*\: *"\(.*\)".*/\1/')

echo "Bearer $api_key"

Bearer eyJrIjoiV3FzcmQwazNXd1F4ZGQ0SDY0ZzZwcGU3Q2xndUlGV20iLCJuIjoiaW5zdGFsbF9hcGlfa2V5IiwiaWQiOjF9