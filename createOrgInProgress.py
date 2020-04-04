import boto3
import time
import uuid

org = boto3.client('organizations')

def createMasterOrg():

  masterResponse = org.create_organization()
  statusResponse = org.list_create_account_status(
    States=[
      'IN_PROGRESS',
    ],
  )
  
  pring(statusResponse)
  masterAccountId = masterResponse['Organization']['MasterAccountId']
  describeResponse = org.describe_account(
    AccountId = masterAccountId
  )
  print(describeResponse)
  
  listRoots = org.list_roots()
  
  return listRoots['Roots'][0]['Id']


def createAccount(accountEmail, accountName):

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
      print("account %s is being created, status: %s" %(accountName, accountStatus['CreateAccountStatus']['State'] ))
    elif accountStatus['CreateAccountStatus']['State'] == 'SUCCEEDED':
      accountId= accountStatus['CreateAccountStatus']['AccountId']
      print("account %s is successfully created, status: %s" %(accountName, accountStatus['CreateAccountStatus']['State'] ))
      print(accountId)
      return accountId



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

    lambdaClient = boto3.client('lambda')
    deleteResponse = lambdaClient.delete_function(
      FunctionName='createAccount'
    )
    print(deleteResponse)


def lambda_handler(event, context):
  loggingAccountEmail = event['ResourceProperties']['LoggingEmail']
  # devAccountEmail =event['ResourceProperties']['DevEmail']
  # stagingAccountEmail =event['ResourceProperties']['StagingEmail']
  # prodAccountEmail =event['ResourceProperties']['ProdEmail']

  if(event['RequestType'] == 'Create'):
    print ("Test event is configured correctly, ex first email: %s" %(loggingAccountEmail))

    masterId = createMasterOrg()
    print("Master org successfully created, id: %s " %(masterId))

    # loggingAccountId = createAccount(loggingAccountEmail, 'Logging')


    
    respond_cloudformation(event, "SUCCESS", {})

  if(event['RequestType'] == 'Update'):
    respond_cloudformation(event, "SUCCESS", {})
  elif(event['RequestType'] == 'Delete'):
    delete_respond_cloudformation(event, "SUCCESS", {})
