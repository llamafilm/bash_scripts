#!/usr/bin/env python3

import boto3
import sys
import time
import os
import socket
from contextlib import closing

session = boto3.Session(profile_name='work')

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False

def startInstance():
  # get Name tag
  for tag in i.tags:
    if tag['Key'] == 'Name':
      instanceName = tag['Value']
  print('Starting instance ' + i.instance_id + ' (' + instanceName + ') ...')

  state = i.state['Name']
  if state == 'running':
    print('Instance is already running')
    return
  elif state in ['pending', 'shutting-down', 'stopping']:
    print('Instance is currently ' + state + '. Please try again later.')
    sys.exit()  
  else:
    i.start()
    if i.state['Name'] != 'pending':
      print('Error! Could not start instance')
      sys.exit()
    else:
      time.sleep(10)
      i.wait_until_running(WaiterConfig = {'Delay': 2})
      i.reload()
      return

print('Which instance would you like to start?')

# get list of all regions.  All regions takes too long, so we choose a few
"""
allRegions = []
ec2client = boto3.client('ec2')
response = ec2client.describe_regions()
for r in response['Regions']:
  allRegions.append(r['RegionName'])
"""
allRegions = ['us-west-1', 'us-east-1', 'us-west-2']
allInstances = []
print('Showing instances from regions: ', ' '.join(allRegions))

# iterate through region list
for r in allRegions:
  ec2 = boto3.resource('ec2', r)
  # print table describing instances
  for counter, object in enumerate(ec2.instances.all()):
    allInstances.append(object)
    for tag in object.tags:
      if tag['Key'] == 'Name':
        instanceName = tag['Value']
    print('(' + str(len(allInstances)) + ')', r, object.instance_id, '\t', object.instance_type, '\t', 
      object.state['Name'], '\t', instanceName)
print()
# get user input
i = allInstances[ int(input()) - 1 ]
startInstance()
print('Public IP: ' + i.public_ip_address)

# login with SSH using correct username
user = 'centos'
for tag in i.tags:
  if tag['Key'] == 'SSH user':
    user = tag['Value']
    break
command = 'ssh ' + user + '@' + i.public_ip_address
print('Logging in after server is up... ', command)

# wait for open port
while not check_socket(i.public_ip_address,22):
  time.sleep(1)
os.system(command)
os.system('osascript -e "tell application \\"Terminal\\" to set current settings of window 1 to default settings"')
