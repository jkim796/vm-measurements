#!/bin/bash

curl --unix-socket /tmp/firecracker.socket -i  \
    -X PUT 'http://localhost/machine-config' \
    -H 'Accept: application/json'            \
    -H 'Content-Type: application/json'      \
    -d '{
        "vcpu_count": 24,
        "mem_size_mib": 32768,
        "ht_enabled": false
    }'
