import json
import boto3
from uuid import uuid4
import os

lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
sns = boto3.client('sns')

def getEmail(path, accountName):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = False
  )
  
  for param in response['Parameters']:
    if accountName in param['Name']:
      return param['Value']
        

def sendMessage(url, messageBody):
  response = sqs.send_message(
    QueueUrl = url,
    MessageBody = messageBody,
    MessageDeduplicationId= uuid4().hex,
    MessageGroupId='1'
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
  queueUrl = os.environ['NextQueue']
  topicArn = os.environ['SlackArn']
  accountName = event['Records'][0]['body']


  try:
    email = getEmail('/org-assemble/emails', accountName)
    # use accountName.toUppercase() when creating account
    accountId = uuid4().hex
    
    randomName = '/org-assemble/accountIds/' + accountName + '-' + str(uuid4())
    putParameter = ssm.put_parameter(
      Name = randomName,
      Description = 'Account Id',
      Value = accountId,
      Type = 'String'
    ) 

    sendMessage(queueUrl, accountName)
  except:
    slackPublish(topicArn, "failed", lambdaName, None)
  