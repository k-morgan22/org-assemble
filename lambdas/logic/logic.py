import json
import boto3
import logging

ssm = boto3.client('ssm')
org = boto3.client('organizations')
ebridge = boto3.client('events')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

triggerStacksets = True


def getMasterId(path, decryption):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = decryption
  )
  
  for param in response['Parameters']:
    if 'master' in param['Name']:
      master = param['Value']
  return master


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
    

def checkOu():

  isPresent = False
  ous = []

  ouList= org.list_organizational_units_for_parent(
    ParentId = rootId
  )

  for ou in ouList['OrganizationalUnits']:
    ous.append(ou['Name'])

  if 'Security' in ous and 'Workloads' in ous:
    isPresent = True
  
  if(isPresent):
    putEvent("createAccount")


def checkAccount():
  global triggerStacksets

  isSecurityCreated = False
  isWorkloadsCreated = False
  secList = []
  workList = []
    
  securityAccounts = org.list_accounts_for_parent(
    ParentId = securityId
  )
    
  for account in securityAccounts['Accounts']:
    secList.append(account['Name'])
    
  workloadsAccounts = org.list_accounts_for_parent(
    ParentId = workloadsId
  )
    
  for account in workloadsAccounts['Accounts']:
    workList.append(account['Name'])
    
  if 'Logging' in secList:
    isSecurityCreated = True
    
  if 'Dev' in workList and 'Prod' in workList and 'Staging' in workList:
    isWorkloadsCreated = True

  if(isSecurityCreated and isWorkloadsCreated and triggerStacksets):
    putEvent("stackset")
    triggerStacksets = False
  

def putEvent(destination):
  
  if(destination == "stackset"):
    details = {
      "metadata": {
        "service": "assembler-logic",
        "operation": "checkAccount",
        "status": "SUCCEEDED"
      },
      "data": {
        "baseStackName": "log stackset"
      }
    }
    response = ebridge.put_events(
      Entries = [
        {
          'Source': 'assembler-logic',
          'DetailType': 'org-assemble event',
          'Detail': json.dumps(details) 
        }
      ]
    )
  else: 
    accountName = ["dev", "staging", "prod", "logging"]
    details = [{
      "metadata": {
        "service": "assembler-logic",
        "operation": "checkOu",
        "status": "SUCCEEDED"
      },
      "data": {
        "accountName": name 
      }
    }for name in accountName] 
    response = ebridge.put_events(
      Entries = [
        {
          'Source': 'assembler-logic',
          'DetailType': 'org-assemble event',
          'Detail': json.dumps(entry) 
        } for entry in details
      ]
    )

# pre-handler global
rootId = getMasterId('/org-assemble/orgIds', False)
[securityId, workloadsId] = getOuIds('/org-assemble/orgIds', False)


def lambda_handler(event, context):
    
  if event['eventName'] == "CreateOrganizationalUnit":
    checkOu()
  elif event['eventName'] == "MoveAccount":
    if "errorCode" not in event:
      checkAccount()
    else:
      logger.info("Triggered by error")  
