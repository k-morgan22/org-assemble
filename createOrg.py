import boto3
import time
import uuid

def createMasterOrg():
  org = boto3.client('organizations')

  # masterResponse = org.create_organization(
  #   FeatureSet = 'ALL'
  # )
  
  listRoots = org.list_roots()
  
  print(listRoots['Roots'][0]['Id'])
  return listRoots['Roots'][0]['Id']

def createOrgUnit(rootId, ouName):
  org = boto3.client('organizations')

  ouResponse = org.create_organizational_unit(
    ParentId = rootId,
    Name = ouName
  )
  
  print(ouResponse['OrganizationalUnit']['Id'])
  return ouResponse['OrganizationalUnit']['Id']

def createAccount(accountEmail, accountName):
  org = boto3.client('organizations')

  accountResponse = org.create_account(
    Email=accountEmail,
    AccountName=accountName,
    RoleName='OrganizationAccountAccessRole',
    IamUserAccessToBilling='DENY'

  )
  print(accountResponse)

  requestId = accountResponse['CreateAccountStatus']['Id']
  while True:
    accountStatus = org.describe_create_account_status(
      CreateAccountRequestId=requestId
    )
    if accountStatus['CreateAccountStatus']['State'] == 'IN_PROGRESS':
      time.sleep(10)
    elif accountStatus['CreateAccountStatus']['State'] == 'SUCCEEDED':
      accountId= accountStatus['CreateAccountStatus']['AccountId']
      print(accountId)
      return accountId
      break 

def moveAccount(newAccountId, rootId, destinationId):
  org = boto3.client('organizations')

  moveResponse = org.move_account(
    AccountId = newAccountId,
    SourceParentId = rootId,
    DestinationParentId = destinationId
  )
  
def createStackSets():
  cf = boto3.client('cloudformation')
  
  baselineStackName = "account-baseline-" + str(uuid.uuid4())  
  
  baselineStackResponse = cf.create_stack_set(
    StackSetName = baselineStackName,
    Description = 'Baseline for new accounts',
    TemplateURL='https://testing-org-lambda.s3.amazonaws.com/lz-baseline.yml',
    Capabilities= [
      'CAPABILITY_NAMED_IAM'
    ],
    PermissionModel='SERVICE_MANAGED',
    AutoDeployment={
      'Enabled': True,
      'RetainStacksOnAccountRemoval': False
    }
  )
  
  baselineStackStatus = cf.list_stack_sets()['Summaries'][0]['Status']
  print("Baseline StackSet is: " + baselineStackStatus)
  
  loggingStackName = "logging-" + str(uuid.uuid4())  
  
  loggingStackResponse = cf.create_stack_set(
    StackSetName = loggingStackName,
    Description = 'Baseline for centralized logging',
    TemplateURL='https://testing-org-lambda.s3.amazonaws.com/lz-logging.yml',
    PermissionModel='SERVICE_MANAGED',
    AutoDeployment={
      'Enabled': True,
      'RetainStacksOnAccountRemoval': False
    }
  )
  
  loggingStackStatus = cf.list_stack_sets()['Summaries'][1]['Status']
  print("Logging StackSet is: " + loggingStackStatus)
    
  return(baselineStackName,loggingStackName)

  
  
def deployLoggingStack(stackName, ou):
  cf = boto3.client('cloudformation')
  deployLogResponse = cf.create_stack_instances(
    StackSetName=stackName,
    DeploymentTargets={
      'OrganizationalUnitIds': [
        ou
      ]
    },
    Regions=[
      'us-east-1'
    ]
  )
  
  loggingOpId = deployLogResponse['OperationId']
  
  while True:
    deployLogStatus = cf.describe_stack_set_operation(
      StackSetName=stackName,
      OperationId=loggingOpId
    )
    if deployLogStatus['StackSetOperation']['Status'] == 'RUNNING':
      time.sleep(10)
      
    if deployLogStatus['StackSetOperation']['Status'] == 'SUCCEEDED':
      print("Success! Log StackSet deployed.")
      break
    


def deployBaselineStack(stackName, ou):
  cf = boto3.client('cloudformation')
  deployBaseResponse = cf.create_stack_instances(
    StackSetName=stackName,
    DeploymentTargets={
      'OrganizationalUnitIds': [
        ou
      ]
    },
    Regions=[
      'us-east-1'
    ]
  )
  
  baselineOpId = deployBaseResponse['OperationId']
  
  while True:
    deployBaseStatus = cf.describe_stack_set_operation(
      StackSetName=stackName,
      OperationId=baselineOpId
    )
    if deployBaseStatus['StackSetOperation']['Status'] == 'RUNNING':
      time.sleep(10)
      
    if deployBaseStatus['StackSetOperation']['Status'] == 'SUCCEEDED':
      print("Success! Base StackSet deployed.")
      break
    

def respond_cloudformation(event, status, data=None):
    responseBody = {
      'Status': status,
      'Reason': 'just work guy',
      'StackId': event['StackId'],
      'RequestId': event['RequestId'],
      'LogicalResourceId': event['LogicalResourceId'], 
      'Data': data
    }
    print(responseBody)

def delete_respond_cloudformation(event, status, data=None):
    responseBody = {
      'Status': status,
      'Reason': 'just work guy',
      'StackId': event['StackId'],
      'RequestId': event['RequestId'],
      'LogicalResourceId': event['LogicalResourceId'], 
      'Data': data
    }

    lambda_client = get_client('lambda')
    lambda_client.delete_function(FunctionName='createAccount')
    print('deleted')


def lambda_handler(event, context):
  loggingAccountEmail = event['ResourceProperties']['LoggingEmail']
  devAccountEmail =event['ResourceProperties']['DevEmail']
  stagingAccountEmail =event['ResourceProperties']['StagingEmail']
  prodAccountEmail =event['ResourceProperties']['ProdEmail']


  if(event['RequestType'] == 'Create'):
    masterId = createMasterOrg()
    securityId = createOrgUnit(masterId, 'Security')
    workloadId = createOrgUnit(masterId, 'Workloads')
    loggingAccountId = createAccount(loggingAccountEmail, 'Logging')
    devAccountId = createAccount(devAccountEmail, 'Dev')
    stagingAccountId = createAccount(stagingAccountEmail, 'Staging')
    prodAccountId = createAccount(prodAccountEmail, 'Prod')

    moveAccount(loggingAccountId, masterId, securityId)
    moveAccount(devAccountId, masterId, workloadId)
    moveAccount(stagingAccountId, masterId, workloadId)
    moveAccount(prodAccountId, masterId, workloadId)
    
    (baselineStackName,loggingStackName) = createStackSets()
    deployLoggingStack(loggingStackName, securityId)
    deployBaselineStack(baselineStackName, workloadId)
    
    respond_cloudformation(event, "SUCCESS", {})

  if(event['RequestType'] == 'Update'):
    respond_cloudformation(event, "SUCCESS", {})
  elif(event['RequestType'] == 'Delete'):
    delete_respond_cloudformation(event, "SUCCESS", {})
