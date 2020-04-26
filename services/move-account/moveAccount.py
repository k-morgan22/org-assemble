import json
import boto3
import uuid
from uuid import uuid4
import os

lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
sns = boto3.client('sns')

def getaccountId(accountName):
  if(accountName == 'Logging'):
    ssmFilterResponse = ssm.describe_parameters(
      ParameterFilters = [
        {
          'Key':'Name' ,
          'Option':'BeginsWith',
          'Values': [
            '/org-assemble/accountId/Logging-'
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
  elif(accountName == 'Dev'):
    ssmFilterResponse = ssm.describe_parameters(
      ParameterFilters = [
        {
          'Key':'Name' ,
          'Option':'BeginsWith',
          'Values': [
            '/org-assemble/accountId/Dev-'
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
  elif(accountName == 'Staging'):
    ssmFilterResponse = ssm.describe_parameters(
      ParameterFilters = [
        {
          'Key':'Name' ,
          'Option':'BeginsWith',
          'Values': [
            '/org-assemble/accountId/Staging-'
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
  elif(accountName == 'Prod'):
    ssmFilterResponse = ssm.describe_parameters(
      ParameterFilters = [
        {
          'Key':'Name' ,
          'Option':'BeginsWith',
          'Values': [
            '/org-assemble/accountId/Prod-'
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


def slackPublish(arn, param1, param2, param3, status, function):
  payload = {
    "param1": param1, 
    "param2": param2,
    "param3": param3,
    "condition": status,
    "function": function
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
    accountId = getaccountId(accountName)
    rootId = getMasterId()
    [securityId, workloadsId] = getOuIds()

    invoke(nextFunct)
    slackPublish(topicArn, accountName, accountId, rootId, "success", lambdaName)
  except:
    slackPublish(topicArn, accountName, accountId, rootId, "failed", lambdaName)