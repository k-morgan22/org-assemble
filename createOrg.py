import boto3
import time

def createMasterOrg():
  org = boto3.client('organizations')

  # masterResponse = org.create_organization(
  #   FeatureSet = 'ALL'
  # )
  
  listRoots = org.list_roots()

  return listRoots['Roots'][0]['Id']

def createOrgUnit(rootId, ouName):
  org = boto3.client('organizations')

  ouResponse = org.create_organizational_unit(
    ParentId = rootId,
    Name = ouName
  )

  return ouResponse['OrganizationalUnit']['Id']

def createAccount(accountEmail, accountName):
#  accountId = 'None'
  org = boto3.client('organizations')

  accountResponse = org.create_account(
    Email=accountEmail,
    AccountName=accountName,
    RoleName='OrganizationAccountAccessRole',
    IamUserAccessToBilling='DENY'

  )

#  requestId = accountResponse['CreateAccountStatus']['Id']

#  accountStatus = org.describe_create_account_status(
#    CreateAccountRequestId=requestId
#  )

#  accountId = accountStatus['CreateAccountStatus']['AccountId']
  
#  while(accountId is None):
#    accountStatus = org.describe_create_account_status(
#      CreateAccountRequestId=requestId
#    )

#    accountId = accountStatus['CreateAccountStatus']['AccountId']

#  return accountId

progress = accountResponse['CreateAccountStatus']['State']
  test = 'true'
  while(test):
    if(progress == 'IN_PROGRESS'):
      time.sleep(2)
      print(progress)
    else:
      accountId= accountResponse['CreateAccountStatus']['AccountId']
      print(accountId)
      test = false

def moveAccount(newAccountId, rootId, destinationId):
  org = boto3.client('organizations')

  moveResponse = org.move_account(
    AccountId = newAccountId,
    SourceParentId = rootId,
    DestinationParentId = destinationId
  )

def respond_cloudformation(event, status):
    responseBody = {
        'Status': status,
        'PhysicalResourceId': event['ServiceToken'],
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId']
    }

def delete_respond_cloudformation(event, status):
    responseBody = {
        'Status': status,
        'PhysicalResourceId': event['ServiceToken'],
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId']
    }

    lambda_client = get_client('lambda')
    lambda_client.delete_function(FunctionName='createOrg')


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

    respond_cloudformation(event, "SUCCESS")

  if(event['RequestType'] == 'Update'):
    respond_cloudformation(event, "SUCCESS")
  elif(event['RequestType'] == 'Delete'):
    delete_respond_cloudformation(event, "SUCCESS")

