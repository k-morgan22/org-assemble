import json
import boto3
from uuid import uuid4

ssm = boto3.client('ssm')
org = boto3.client('organizations')


def grabMasterId():
  
  listRoots = org.list_roots()
  
  return listRoots['Roots'][0]['Id']


def createOrgUnit(rootId, ouName):

  ouResponse = org.create_organizational_unit(
    ParentId = rootId,
    Name = ouName
  )
  
  return ouResponse['OrganizationalUnit']['Id']
  
  
def putParameter(prefix, description, idValue):
  paramName = prefix + str(uuid4())
  
  ssm.put_parameter(
    Name = paramName,
    Description = description,
    Value = idValue,
    Type = 'String'
  )

# pre-handler global
masterId = grabMasterId()

def lambda_handler(event, context):

  putParameter('/org-assemble/orgIds/master-', 'Master Org Id', masterId )

  workloadsId = createOrgUnit(masterId, "Workloads")
  putParameter('/org-assemble/orgIds/workloads-', 'Workloads Ou Id', workloadsId)
  
  securityId = createOrgUnit(masterId, "Security")
  putParameter('/org-assemble/orgIds/security-', 'Security Ou Id', securityId )