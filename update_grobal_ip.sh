#!/bin/bash


dns_setting_json=`/usr/local/bin/aws lightsail get-domain --domain-name "${MY_DOMAIN}" --region us-east-1 | /usr/bin/jq '.domain.domainEntries[] | select(.name == "home.'"${MY_DOMAIN}"'" and .type == "A")'`
ip=`/usr/bin/curl -4 -s ifconfig.co`
updated_dns_setting_json=$(echo "$dns_setting_json" | /usr/bin/jq --arg new_ip "$ip" '.target = $new_ip')

/usr/local/bin/aws lightsail update-domain-entry --domain-name "${MY_DOMAIN}" --region us-east-1 --domain-entry "$updated_dns_setting_json"

