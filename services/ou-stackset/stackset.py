import json
import boto3
import uuid
from uuid import uuid4
import os

lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
sns = boto3.client('sns')


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


def sendMessage(url, messageBody):
  response = sqs.send_message(
    QueueUrl = url,
    MessageBody = messageBody,
    MessageDeduplicationId= uuid4().hex,
    MessageGroupId='1'
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
  queueUrl = os.environ['NextQueue']
  topicArn = os.environ['SlackArn']


  try:
    [securityId, workloadsId] = getOuIds()

    sendMessage(queueUrl, "stacksets deployed")
    slackPublish(topicArn, queueUrl, securityId, workloadsId, "success", lambdaName)
  except:
    slackPublish(topicArn, queueUrl, securityId, workloadsId, "failed", lambdaName)