import boto3
import sys
import time
import os
import socket
from contextlib import closing

session = boto3.Session(profile_name='work')
ec2 = session.client('ec2')

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False

def startInstance(instanceID):
  response = ec2.describe_instances(InstanceIds=[instanceID])['Reservations'][0]['Instances'][0]

  for tags in response['Tags']:
    if tags['Key'] == 'Name':
      instanceName = tags['Value']
  print('Starting instance ' + instanceID + ' (' + instanceName + ') ...')

  state = response['State']['Name']
  if state == "running":
    print('Instance is already running')
    response = ec2.describe_instances(InstanceIds=[instanceID])['Reservations'][0]['Instances'][0]
    return response['PublicIpAddress']
  elif state in ['pending', 'shutting-down', 'stopping']:
    print('Instance is currenting ' + state + '. Please try again later.')
    sys.exit()  
  else:
    response = ec2.start_instances(InstanceIds=[instanceID])['StartingInstances']
    if response[0]['CurrentState']['Name'] != 'pending':
      print('Error! Could not start instance')
      sys.exit()
    else:
      while True:
        response = ec2.describe_instances(InstanceIds=[instanceID])['Reservations'][0]['Instances'][0]
        if response['State']['Code'] == 16:
          return response['PublicIpAddress']
        time.sleep(1)

print('Which instance would you like to start?')

# print table describing instances
response = ec2.describe_instances()['Reservations']
for counter, i in enumerate(response):
  for tags in i['Instances'][0]['Tags']:
    if tags['Key'] == 'Name':
      instanceName = tags['Value']
  print('(' + str(counter) + ')', i['Instances'][0]['InstanceId'] + '\t' + 
    i['Instances'][0]['InstanceType'] + '\t' + i['Instances'][0]['State']['Name'] + '\t\t' + instanceName)

# get user input
print()
choice = int(input())

publicIP = startInstance(response[choice]['Instances'][0]['InstanceId'])
print('Public IP: ' + publicIP)

# login with SSH using correct username
user = 'centos'
for tags in response[choice]['Instances'][0]['Tags']:
  print(tags)
  if tags['Key'] == 'SSH user':
    user = tags['Value']
    break
command = 'ssh ' + user + '@' + publicIP
print('Logging in after ping is up... ', command)

# wait for open port
while not check_socket(publicIP,22):
  time.sleep(1)
os.system(command)
os.system('osascript -e "tell application \\"Terminal\\" to set current settings of window 1 to default settings"')
