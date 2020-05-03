import json
import boto3
from uuid import uuid4
import os



sns = boto3.client('sns')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
org = boto3.client('organizations')


def getMasterId(path, decryption):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = decryption
  )
  
  for param in response['Parameters']:
    if 'master' in param['Name']:
      master = param['Value']
  return master


def getOuIds(path, decryption):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = decryption
  )
  
  for param in response['Parameters']:
    if 'security' in param['Name']:
      security = param['Value']
    elif 'workloads' in param['Name']:
      workloads = param['Value']
  return security, workloads
    

def checkOu(QueueName, snsArn):
  rootId = getMasterId('/org-assemble/orgIds', False)

  isPresent = False
  ous = []

  ouList= org.list_organizational_units_for_parent(
    ParentId = rootId
  )

  for ou in ouList['OrganizationalUnits']:
    ous.append(ou['Name'])
 
  if 'Security' in ous and 'Workloads' in ous:
    isPresent = True
  
  if(isPresent):
    sendMessages(4, QueueName)
    slackPublish(snsArn, "success", None, "Security & Workloads organizational units have been created")




def checkAccount(QueueName, snsArn):
  [securityId, workloadsId] = getOuIds('/org-assemble/orgIds', False)
  
  isSecurityCreated = False
  isWorkloadsCreated = False
  secList = []
  workList = []
    
  securityAccounts = org.list_accounts_for_parent(
    ParentId = securityId
  )
    
  for account in securityAccounts['Accounts']:
    secList.append(account['Name'])
    
  workloadsAccounts = org.list_accounts_for_parent(
    ParentId = workloadsId
  )
    
  for account in workloadsAccounts['Accounts']:
    workList.append(account['Name'])
    
  if 'Logging' in secList:
    isSecurityCreated = True
    
  if 'Dev' in workList and 'Prod' in workList and 'Staging' in workList:
    isWorkloadsCreated = True

  if(isSecurityCreated and isWorkloadsCreated):
    sendMessages(1, QueueName)
    slackPublish(snsArn, "success", None, "All accounts created and moved to the correct Organizational Unit")



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
    messageBody = ["dev", "staging", "prod", "logging"]
    messages_list = [messageFormat(each) for each in messageBody]
    
    response = sqs.send_message_batch(
      QueueUrl = url,
      Entries = [{'Id': message['id'], 'MessageBody': message['string'],'MessageDeduplicationId': message['id'],'MessageGroupId': '1'} for message in messages_list]
    )
    
def slackPublish(arn, status, function, text):
  payload = {
    "condition": status,
    "function": function,
    "text": text
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
      checkOu(queueUrl, topicArn)
    elif(event['origin'] == 'moveAccount'):
      checkAccount(secondUrl,topicArn)

  except:
    slackPublish(topicArn, "failed", lambdaName, None)
  
