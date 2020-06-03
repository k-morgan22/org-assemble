import json
import boto3
from uuid import uuid4
import os
import time

lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
sns = boto3.client('sns')
cf = boto3.client('cloudformation')


# business logic

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


def createBaseStack():
  
  baselineStackName = "account-baseline-" + str(uuid4())  
  
  baselineStackResponse = cf.create_stack_set(
    StackSetName = baselineStackName,
    Description = 'Baseline for new accounts',
    TemplateURL='https://testing-org-lambda.s3.amazonaws.com/accountBase.yml',
    Capabilities= [
      'CAPABILITY_NAMED_IAM'
    ],
    PermissionModel='SERVICE_MANAGED',
    AutoDeployment={
      'Enabled': True,
      'RetainStacksOnAccountRemoval': False
    }
  )
  
  return baselineStackName
  
def createLogStack():  

  loggingStackName = "logging-baseline-" + str(uuid4())  
  
  loggingStackResponse = cf.create_stack_set(
    StackSetName = loggingStackName,
    Description = 'Baseline for centralized logging',
    TemplateURL='https://testing-org-lambda.s3.amazonaws.com/securityBase.yml',
    PermissionModel='SERVICE_MANAGED',
    AutoDeployment={
      'Enabled': True,
      'RetainStacksOnAccountRemoval': False
    }
  )
  
  return loggingStackName

  
def deployLoggingStack(stackName, ou):
  deployLogResponse = cf.create_stack_instances(
    StackSetName=stackName,
    DeploymentTargets={
      'OrganizationalUnitIds': [
        ou
      ]
    },
    Regions=[
      'us-east-1'
    ],
    OperationPreferences={
      'FailureTolerancePercentage': 100,
      'MaxConcurrentPercentage': 100
    }
  )
  
  loggingOpId = deployLogResponse['OperationId']
  
  while True:
    deployLogStatus = cf.describe_stack_set_operation(
      StackSetName=stackName,
      OperationId=loggingOpId
    )

    if deployLogStatus['StackSetOperation']['Status'] == 'RUNNING':
      time.sleep(2)
    elif deployLogStatus['StackSetOperation']['Status'] == 'SUCCEEDED':  
      break
    


def deployBaselineStack(stackName, ou):
  deployBaseResponse = cf.create_stack_instances(
    StackSetName=stackName,
    DeploymentTargets={
      'OrganizationalUnitIds': [
        ou
      ]
    },
    Regions=[
      'us-east-1'
    ],
    OperationPreferences={
      'FailureTolerancePercentage': 100,
      'MaxConcurrentPercentage': 100
    }
  )
  
  baselineOpId = deployBaseResponse['OperationId']
  
  while True:
    deployBaseStatus = cf.describe_stack_set_operation(
      StackSetName=stackName,
      OperationId=baselineOpId
    )
    if deployBaseStatus['StackSetOperation']['Status'] == 'RUNNING':
      time.sleep(2)
    elif deployBaseStatus['StackSetOperation']['Status'] == 'SUCCEEDED':
      break


# communication logic

def invoke():
  payload = {
    "origin": "stackset"
  }

  response = lambdaClient.invoke(
    FunctionName = 'logic',
    InvocationType = 'Event',
    LogType = 'None',
    Payload = json.dumps(payload)
  )

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
  stack = event['Records'][0]['body']


  try:
    if(stack == 'log stack'):
      securityId, workloadsId = getOuIds('/org-assemble/orgIds', False)
      loggingStackName = createLogStack()
      deployLoggingStack(loggingStackName, securityId)
      
      invoke()
      slackPublish(topicArn, "success", None, "Security baseline deployed")
    elif(stack == 'base stack'):
      securityId, workloadsId = getOuIds('/org-assemble/orgIds', False)
      envStackName = createBaseStack()
      deployBaselineStack(envStackName, workloadsId)
  
      sendMessage(queueUrl, "stacksets deployed")
      slackPublish(topicArn, "success", None, "Env Account baselines deployed")
  except:
    slackPublish(topicArn, "failed", lambdaName, None)