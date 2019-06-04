#!/usr/bin/env python3

import boto3
import sys
import time
import os
import socket
from contextlib import closing


session = boto3.Session(profile_name='work')
ec2 = session.resource('ec2')

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False

def startInstance(i):
  # get Name tag
  for tag in i.tags:
    if tag['Key'] == 'Name':
      instanceName = tag['Value']
  print('Starting instance ' + i.instance_id + ' (' + instanceName + ') ...')

  state = i.state['Name']
  if state == 'running':
    print('Instance is already running')
    return i.public_ip_address
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
      return i.public_ip_address

print('Which instance would you like to start?')

# print table describing instances
list = []
for counter, object in enumerate(ec2.instances.all()):
  list.append(object)
  for tag in object.tags:
    if tag['Key'] == 'Name':
      instanceName = tag['Value']
  print('(' + str(counter) + ')', object.instance_id + '\t' + object.instance_type + '\t' + 
    object.state['Name'] + '\t\t' + instanceName)
# get user input
print()
choice = int(input())

publicIP = startInstance(list[choice])
print('Public IP: ' + publicIP)

# login with SSH using correct username
user = 'centos'
for tag in list[choice].tags:
  if tag['Key'] == 'SSH user':
    user = tag['Value']
    break
command = 'ssh ' + user + '@' + publicIP
print('Logging in after server is up... ', command)

# wait for open port
while not check_socket(publicIP,22):
  time.sleep(1)
os.system(command)
os.system('osascript -e "tell application \\"Terminal\\" to set current settings of window 1 to default settings"')
