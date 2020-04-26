import json
import boto3
from uuid import uuid4



cf = boto3.client('cloudformation')
sqs = boto3.client('sqs')
org = boto3.client('organizations')

def checkOu():
  isPresent = False
  
  ouList= org.list_organizational_units_for_parent(
    ParentId = rootId
  )
  
  ou1 = ouList['OrganizationalUnits'][0]['Name']
  ou2 = ouList['OrganizationalUnits'][1]['Name']
  
  if ((ou1 in ['Security', 'Workloads']) and (ou2 in ['Security', 'Workloads'])):
    print("both ous are present")
    isPresent = True
  
  if(isPresent):
    sendMessages(4, "ous created", QueueName)


def checkAccount():
  isSecurityCreated = False
  isWorkloadsCreated = False
    
  securityAccounts = org.list_accounts_for_parent(
    ParentId = securityId
  )
    
  s1 = securityAccounts['Accounts'][0]['Name']

    
  workloadsAccounts = org.list_accounts_for_parent(
    ParentId = workloadsId
  )
    
  w1 = workloadsAccounts['Accounts'][0]['Name']
  w2 = workloadsAccounts['Accounts'][1]['Name']
  w3 = workloadsAccounts['Accounts'][2]['Name']

    
    
  if(s1 == 'Logging'):
    print('logging in correct ou')
    isSecurityCreated = True
    
  if((w1 in ['Prod', 'Dev', 'Staging']) and (w2 in ['Prod', 'Dev', 'Staging']) and (w3 in ['Prod', 'Dev', 'Staging'])):
    print('prod, dev, and staging in correct ou')
    isWorkloadsCreated = True

  if(isSecurityCreated and isWorkloadsCreated):
    sendMessages(1, "accounts created", QueueName)
    print('message sent')
  

def messageFormat(body):
  message = {
    'id': uuid4().hex,
    'string': body
  }
  return message    

def sendMessages(entries, messageBody, url):
  if (entries == 1):
    response = sqs.send_message(
      QueueUrl = url,
      MessageBody = messageBody,
      MessageDeduplicationId= uuid4().hex,
      MessageGroupId='1'
    )
  else:
    messages_list = [messageFormat(messageBody) for each in range(0,entries)]
    
    response = sqs.send_message_batch(
      QueueUrl = url,
      Entries = [{'Id': message['id'], 'MessageBody': message['string'],'MessageDeduplicationId': message['id'],'MessageGroupId': '1'} for message in messages_list]
    )
    


def lambda_handler(event, context):
  if(event['origin'] == 'createOu'):
    checkOu()
  elif(event['origin'] == 'moveAccount'):
    checkAccount()
  else:
    print('something went wrong')

  