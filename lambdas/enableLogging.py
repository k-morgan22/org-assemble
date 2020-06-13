import json
import boto3

org = boto3.client('organizations')
trail = boto3.client('cloudtrail')

def getAccountIds():
  envList = []
  response = org.list_accounts()
  for account in response['Accounts']:
    if account['Name'] == "Logging":
      logging = account['Id']
    elif account['Name'] in ["Dev", "Staging", "Prod"]:
      envList.append(account['Id'])
  
  return envList, logging

def isOrg():
  orgEnabled = False
  response = trail.describe_trails(
    includeShadowTrails = False
  )
  cloudtrail = response['trailList'][0]
  if cloudtrail['IsOrganizationTrail'] == True:
    orgEnabled = True
  trailName = cloudtrail['Name']
  
  return orgEnabled, trailName

def updateTrail(trailName, newBucket):
  response = trail.update_trail(
    Name = trailName,
    S3BucketName = newBucket,
    IsOrganizationTrail = True
  )

def updateBucket(trailName, newBucket):
  response = trail.update_trail(
    Name = trailName,
    S3BucketName = newBucket
  )


def addEvent(trailName, buckets):
  response = trail.put_event_selectors(
    TrailName = trailName,
    EventSelectors = [
      {
        'DataResources': [
          {
            'Type': 'AWS::S3::Object',
            'Values': buckets
          }
        ]
      }
    ]
  )

def lambda_handler(event, context):
  envAccounts, logAccount = getAccountIds()
  logBucket = f"cloudtrail-logs-{logAccount}" 
  envBuckets =[f"arn:aws:s3:::bucket-{account}/" for account in envAccounts]

  trailAccess = org.enable_aws_service_access(
    ServicePrincipal='cloudtrail.amazonaws.com'
  )

  orgEnabled, trailName = isOrg()

  if(orgEnabled != True):
    updateTrail(trailName, logBucket)
  else: 
    updateBucket(trailName, logBucket)

  addEvent(trailName, envBuckets)
