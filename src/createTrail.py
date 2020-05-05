import json
import boto3
import os

lambdaClient = boto3.client('lambda')
ssm = boto3.client('ssm')
sns = boto3.client('sns')
sts = boto3.client('sts')
org = boto3.client('organizations')
trail = boto3.client('cloudtrail')

# business logic

def getAccountIds(path, decryption):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = decryption
  )
  
  envList = []
  
  for param in response['Parameters']:
    if 'logging' in param['Name']:
      logging = param['Value']
    else:
      envList.append(param['Value'])
  
  return envList, logging
  
def createTrail(trailName, bucketName):
  trailAccess = org.enable_aws_service_access(
    ServicePrincipal='cloudtrail.amazonaws.com'
  )

  create = trail.create_trail(
    Name = trailName,
    S3BucketName = bucketName,
    IncludeGlobalServiceEvents = True,
    IsMultiRegionTrail = True,
    EnableLogFileValidation = True,
    IsOrganizationTrail = True
  )

  startLogging = trail.start_logging(
    Name = trailName
  )

def addEvents(trailName, buckets):
  addEvents = trail.put_event_selectors(
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
  
  
 
 # communication logic
 
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
  topicArn = os.environ['SlackArn']


  try:
    envAccounts, logAccount = getAccountIds('/org-assemble/accountIds', False)
    trailName = "organization-trail-DO-NOT-DELETE"
    logBucket = f'{logAccount}-cloudtrail-logs-do-not-delete'
    accountBuckets = [f'arn:aws:s3:::{account}-storage-bucket/' for account in envAccounts]
    
    createTrail(trailName, logBucket)
    addEvents(trailName, accountBuckets)

    
    slackPublish(topicArn, "success", None, "Organization Trail started logging")
  except:
    slackPublish(topicArn, "failed", lambdaName, None)