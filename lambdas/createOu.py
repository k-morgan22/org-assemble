import json
import boto3
from uuid import uuid4
import os

lambdaClient = boto3.client('lambda')
ssm = boto3.client('ssm')
sns = boto3.client('sns')
org = boto3.client('organizations')

#business logic

def grabMasterId():
  
  listRoots = org.list_roots()
  
  return listRoots['Roots'][0]['Id']


def createOrgUnit(rootId, ouName):

  ouResponse = org.create_organizational_unit(
    ParentId = rootId,
    Name = ouName
  )
  
  return ouResponse['OrganizationalUnit']['Id']

#communication logic

def invoke(funct):
  payload = {
    "origin": "createOu"
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
  topicArn = os.environ['SlackArn']
  nextFunct = os.environ['InvokeLambda']


  try:
    
    masterId = grabMasterId()
    masterName = '/org-assemble/orgIds/master-'+ str(uuid4())
    
    putParameter = ssm.put_parameter(
      Name = masterName,
      Description = 'Master Org Id',
      Value = masterId,
      Type = 'String'
    )
  
    securityId = createOrgUnit(masterId, "Security")
    workloadsId = createOrgUnit(masterId, "Workloads")
    
    securityName = '/org-assemble/orgIds/security-'+ str(uuid4())
    putParameter = ssm.put_parameter(
      Name = securityName,
      Description = 'Security Ou Id',
      Value = securityId,
      Type = 'String'
    )
    
    workloadsName = '/org-assemble/orgIds/workloads-'+ str(uuid4())
    putParameter = ssm.put_parameter(
      Name = workloadsName,
      Description = 'Workloads Ou Id',
      Value = workloadsId,
      Type = 'String'
    )

    invoke(nextFunct)
  except:
    slackPublish(topicArn, "failed", lambdaName, None)