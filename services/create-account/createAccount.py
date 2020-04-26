import json
import boto3
import uuid
from uuid import uuid4
import os

lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
sns = boto3.client('sns')

def getEmail(accountName):
  if(accountName == 'Logging'):
    ssmFilterResponse = ssm.describe_parameters(
      ParameterFilters = [
        {
          'Key':'Name' ,
          'Option':'BeginsWith',
          'Values': [
            '/org-assemble/emails/logging-'
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
            '/org-assemble/emails/dev-'
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
            '/org-assemble/emails/staging-'
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
            '/org-assemble/emails/prod-'
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
  accountName = event['Records'][0]['body']


  try:
    email = getEmail(accountName)
    accountId = '43143143141'
    
    randomName = '/org-assemble/accountId/' + accountName + '-' + str(uuid.uuid4())
    putParameter = ssm.put_parameter(
      Name = randomName,
      Description = 'Account Id',
      Value = accountId,
      Type = 'String'
    )

    sendMessage(queueUrl, accountName)
    slackPublish(topicArn, accountName, email, randomName, "success", lambdaName)
  except:
    slackPublish(topicArn, accountName, email, randomName, "failed", lambdaName)