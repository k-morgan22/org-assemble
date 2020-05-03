import json
import boto3
from uuid import uuid4
import os

lambdaClient = boto3.client('lambda')
ssm = boto3.client('ssm')
sns = boto3.client('sns')

def getaccountId(path, accountName):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = False
  )
  
  for param in response['Parameters']:
    if accountName in param['Name']:
      return param['Value']


def getOrgIds(path, decryption):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = decryption
  )
  
  for param in response['Parameters']:
    if 'master' in param['Name']:
      master = param['Value']
    elif 'security' in param['Name']:
      security = param['Value']
    elif 'workloads' in param['Name']:
      workloads = param['Value']
  return master, security, workloads

def invoke(funct):
  payload = {
    "origin": "moveAccount"
  }

  response = lambdaClient.invoke(
    FunctionName = funct,
    InvocationType = 'Event',
    LogType = 'None',
    Payload = json.dumps(payload)
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
  lambdaName = os.environ['LambdaName']
  nextFunct = os.environ['InvokeLambda']
  topicArn = os.environ['SlackArn']
  accountName = event['Records'][0]['body']



  try:
    accountId = getaccountId('/org-assemble/accountId', accountName)
    [masterId, securityId, workloadsId] = getOrgIds('/org-assemble/orgIds', False)


    invoke(nextFunct)
  except:
    slackPublish(topicArn, "failed", lambdaName, None)