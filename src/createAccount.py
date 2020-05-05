import json
import boto3
from uuid import uuid4
import os
import time

lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
sns = boto3.client('sns')
org = boto3.client('organizations')


# business logic

def getEmail(path, accountName):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = False
  )
  
  for param in response['Parameters']:
    if accountName in param['Name']:
      return param['Value']
        


def createAccount(accountEmail, accountName):

  accountResponse = org.create_account(
    Email=accountEmail,
    AccountName=accountName,
    RoleName='OrganizationAccountAccessRole',
    IamUserAccessToBilling='DENY'

  )

  requestId = accountResponse['CreateAccountStatus']['Id']
  while True:
    accountStatus = org.describe_create_account_status(
      CreateAccountRequestId=requestId
    )
    if accountStatus['CreateAccountStatus']['State'] == 'IN_PROGRESS':
      time.sleep(2)
    elif accountStatus['CreateAccountStatus']['State'] == 'SUCCEEDED':
      accountId= accountStatus['CreateAccountStatus']['AccountId']
      return accountId


# communication logic

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
    accountId = createAccount(email, accountName.capitalize())

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