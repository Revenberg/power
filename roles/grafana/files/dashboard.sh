api_key=$1
dashboard=$(cat $2)

curl -H "Authorization: $api_key" -H 'Content-Type: application/json' http://localhost:3000/api/dashboards/db -XPOST -d "$dashboard"