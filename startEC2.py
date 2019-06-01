import boto3
import sys
import time

session = boto3.Session(profile_name='work')
ec2 = session.client('ec2')

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
    print('Public IP: ' + response['PublicIpAddress'])
    sys.exit()
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
          print('Public IP: ' + response['PublicIpAddress'])
          break
        time.sleep(1)
      sys.exit()

print('Which instance would you like to start?')

response = ec2.describe_instances()['Reservations']
for counter, i in enumerate(response):
  for tags in i['Instances'][0]['Tags']:
    if tags['Key'] == 'Name':
      instanceName = tags['Value']
  print('(' + str(counter) + ')', i['Instances'][0]['InstanceId'] + '\t' + 
    i['Instances'][0]['InstanceType'] + '\t' + i['Instances'][0]['State']['Name'] + '\t\t' + instanceName)

print()
choice = int(input())

startInstance(response[choice]['Instances'][0]['InstanceId'])
