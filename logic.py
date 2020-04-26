import json
import boto3
from uuid import uuid4
import os



sns = boto3.client('sns')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
org = boto3.client('organizations')


def getMasterId():
  ssmFilterResponse = ssm.describe_parameters(
    ParameterFilters = [
      {
        'Key':'Name' ,
        'Option':'BeginsWith',
        'Values': [
          '/org-assemble/masterId/master-'
        ]
      },
    ],
    MaxResults = 1
  )
  
  paramName = ssmFilterResponse['Parameters'][0]['Name']
  
  filteredParam = ssm.get_parameter(
    Name = paramName
  )
  param = filteredParam['Parameter']['Value']
  return param

def getOuIds():
  securityFilterResponse = ssm.describe_parameters(
    ParameterFilters = [
      {
        'Key':'Name' ,
        'Option':'BeginsWith',
        'Values': [
          '/org-assemble/ouId/security-'
        ]
      },
    ],
    MaxResults = 1
  )
  
  securityParamName = securityFilterResponse['Parameters'][0]['Name']
  
  securityFilteredParam = ssm.get_parameter(
    Name = securityParamName
  )
  securityParam = securityFilteredParam['Parameter']['Value']

  workloadsFilterResponse = ssm.describe_parameters(
    ParameterFilters = [
      {
        'Key':'Name' ,
        'Option':'BeginsWith',
        'Values': [
          '/org-assemble/ouId/workloads-'
        ]
      },
    ],
    MaxResults = 1
  )
  
  workloadsParamName = workloadsFilterResponse['Parameters'][0]['Name']
  
  workloadsFilteredParam = ssm.get_parameter(
    Name = workloadsParamName
  )
  workloadsParam = workloadsFilteredParam['Parameter']['Value']
  return securityParam, workloadsParam


def checkOu(QueueName):
  rootId = getMasterId()
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
    sendMessages(4, QueueName)


def checkAccount(QueueName):
  [securityId, workloadsId] = getOuIds()
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
    sendMessages(1, QueueName)
    print('message sent')
  

def messageFormat(body):
  message = {
    'id': uuid4().hex,
    'string': body
  }
  return message    

def sendMessages(entries, url):
  if (entries == 1):
    response = sqs.send_message(
      QueueUrl = url,
      MessageBody = "accounts created",
      MessageDeduplicationId= uuid4().hex,
      MessageGroupId='1'
    )
  else:
    messageBody = ["Dev", "Staging", "Prod", "Logging"]
    messages_list = [messageFormat(each) for each in messageBody]
    
    response = sqs.send_message_batch(
      QueueUrl = url,
      Entries = [{'Id': message['id'], 'MessageBody': message['string'],'MessageDeduplicationId': message['id'],'MessageGroupId': '1'} for message in messages_list]
    )
    

def slackPublish(arn, param1, status, function):
  payload = {
    "param1": param1, 
    "condition": status,
    "function": function
  }
  response = sns.publish(
    TopicArn = arn, 
    Message=json.dumps({'default': json.dumps(payload)}),
    MessageStructure='json'
  ) 

def lambda_handler(event, context):
  queueUrl = os.environ['NextQueue']
  secondUrl = os.environ['SecondQueue']
  lambdaName = os.environ['LambdaName']
  topicArn = os.environ['SlackArn']

  try:
    if(event['origin'] == 'createOu'):
      checkOu(queueUrl)
    elif(event['origin'] == 'moveAccount'):
      checkAccount(secondUrl)


    slackPublish(topicArn, queueUrl, "success", lambdaName)
  except:
    slackPublish(topicArn, queueUrl, "failed", lambdaName)



  