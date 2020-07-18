import boto3
import logging

ssm = boto3.client('ssm')
org = boto3.client('organizations')

#initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def getOrgIds(path, decryption):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = decryption
  )
  
  for param in response['Parameters']:
    if 'master' in param['Name']:
      master = param['Value']
    elif 'security' in param['Name']:
      security = param['Value']
    elif 'workloads' in param['Name']:
      workloads = param['Value']
  return master, security, workloads


def grabName(accountId):
  response = org.describe_account(
    AccountId = accountId
  )

  accountName = response['Account']['Name']
  return accountName


def moveAccount(newAccountId, rootId, destinationId):

  moveResponse = org.move_account(
    AccountId = newAccountId,
    SourceParentId = rootId,
    DestinationParentId = destinationId
  )


def lambda_handler(event, context):
  masterId, securityId, workloadsId = getOrgIds('/org-assemble/orgIds', False)
  
  accountId = event['accountId']
  accountName = grabName(accountId)

  if accountName == "Logging":
    moveAccount(accountId, masterId, securityId)
  elif accountName in ["Dev", "Staging", "Prod"]:  
    moveAccount(accountId, masterId, workloadsId)
  else:
    logger.info("Accidental Trigger")