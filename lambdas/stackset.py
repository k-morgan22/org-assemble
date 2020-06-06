import json
import boto3
from uuid import uuid4
import time
import logging

ssm = boto3.client('ssm')
cf = boto3.client('cloudformation')
ebridge = boto3.client('events')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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


def createBaseStack(name, url ):
  try:
    baselineStackName = name + str(uuid4())  
  
    baselineStackResponse = cf.create_stack_set(
      StackSetName = baselineStackName,
      Description = 'Baseline for new accounts',
      TemplateURL= url,
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
  except Exception as e:
    logger.error(e)
    raise
  


def deployBaselineStack(stackName, ou):
  try:
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
        'FailureTolerancePercentage': 0,
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
        time.sleep(10)
      elif deployBaseStatus['StackSetOperation']['Status'] == 'SUCCEEDED':
        break
  except Exception as e:
    logger.error(e)
    raise
  

def putEvent(destination):
  
  if(destination == "stackset"):
    details = {
      "metadata": {
        "service": "assembler-stackset",
        "operation": "stackset-logBase",
        "status": "SUCCEEDED"
      },
      "data": {
        "baseStackName": "account stackset"
      }
    }
  else:
    details = {
      "metadata": {
        "service": "assembler-stackset",
        "operation": "stackset-accountBase",
        "status": "SUCCEEDED"
      },
      "data": {
        "randomData": "placeholder"
      }
    }
  response = ebridge.put_events(
    Entries = [
      {
        'Source': 'assembler-stackset',
        'DetailType': 'org-assemble event',
        'Detail': json.dumps(details) 
      }
    ]
  )


#pre-handler global var
securityId, workloadsId = getOuIds('/org-assemble/orgIds', False)	

def lambda_handler(event, context):
  if event['baseStackName'] == "log stackset":
    loggingStackName = createBaseStack("logging-baseline-", 'https://testing-org-lambda.s3.amazonaws.com/securityBase.yml')
    deployBaselineStack(loggingStackName, securityId)

    putEvent("stackset")

  elif event['baseStackName'] == "account stackset":
    envStackName = createBaseStack("account-baseline-", 'https://testing-org-lambda.s3.amazonaws.com/accountAssembleBase.yml')
    deployBaselineStack(envStackName, workloadsId)

    putEvent("enableLogging")