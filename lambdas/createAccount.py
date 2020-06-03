import json
import boto3

ssm = boto3.client('ssm')
org = boto3.client('organizations')


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

def lambda_handler(event, context):
  accountName = event['accountName']

  email = getEmail('/org-assemble/emails', accountName)
  createAccount(email, accountName.capitalize())
