#!/bin/bash

# Monitor mode for job control, allows fg in the last line
set -o monitor

# Reads RabbitMQ environment and starts server in the backgroun
sudo -u nobody configurable-http-proxy --api-ip ${HOSTNAME} &> /var/log/chp.log &

logfile=/var/log/chp.log

echo "=> Redirecting log file $logfile to stdout"
(
    tail -F /var/log/chp.log | while read line ; do
        echo $line
    done
) &

#echo "=> Starting crond"
#/usr/sbin/cron

echo "=> Starting configsync.py in the background"
/configsync.py & fg %1 > /dev/null
