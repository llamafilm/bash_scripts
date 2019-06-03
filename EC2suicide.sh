#!/bin/bash
# This systemd service will shutdown the computer if there is no active SSH connection after a time period
# We will also publish SNS message to the EC2-alerts topic
# dependencies: jq, curl, awscli accessible to root user
# requires AWS permission to publish SNS

timeout=300
logfile="/var/log/suicide.txt"
topic_arn="changeme"
region=$(curl -sN http://169.254.169.254/latest/dynamic/instance-identity/document | jq '.region' -r 2>&1) || { region="us-west-1"; echo "jq not found.  Defaulting to us-west-1."; }

echo "Starting up with timeout set to $timeout"
date >> $logfile
conn=1

myID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id/)
myName=$(aws --region us-west-1 ec2 describe-tags --filter "Name=resource-id,Values=$myID" --query 'Tags[?Key==`Name`].Value' --output text)
message="Shutting down instance $myID ($myName) due to $timeout seconds of SSH inactivity"
command -v aws >/dev/null || echo "Error: could not find aws cli"

isConnected() {
  while read line; do
    if [ $line == "ESTAB" ]; then
      return 0
    fi
  done < <(ss -Htn | awk '$4 ~ /:22/ {print $1}')
  return 1
}

while true; do
  if isConnected; then
    conn=1
  else
    if [ $conn == 0 ]; then
      echo "$message" >> $logfile
      aws sns publish --region "$region" --topic-arn "$topic_arn" --subject "EC2 Instance Suicide ($myName)" --message "$message"
      shutdown now
    fi
    conn=0
  fi
  sleep $timeout
done
