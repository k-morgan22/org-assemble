from crhelper import CfnResource
import boto3
import json
import os

helper = CfnResource()
ebridge = boto3.client('events')
trail = boto3.client('cloudtrail')
s3 = boto3.client('s3')
org = boto3.client('organizations')


@helper.create
def create(event, context):
  accountId = os.environ['accountId']
    
  trailExists, trailName  = checkTrail()
  if trailExists:
    checkLogging(trailName)
  else:
    createTrail(accountId)

  putEvent()

@helper.update
@helper.delete
def no_op(_, __):
    pass


def checkTrail():
  exists = False
  response = trail.list_trails()
  if response['Trails']: 
    exists = True
    name = response['Trails'][0]['Name']
  else: 
    name = None

  return exists, name

def checkLogging(name):
  response = trail.get_trail_status(
    Name = name
  )
  
  logging = response['IsLogging']
  if logging:
    return
  else:
    trail.start_logging(
      Name = name
    )
  
def createTrail(accountId):  
  bucketName = f"cloudtrail-logs-{accountId}"
  
  createBucket = s3.create_bucket(
    Bucket = bucketName
  )
  
  policy = {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "AWSCloudTrailAclCheck",
        "Effect": "Allow",
        "Principal": {"Service": "cloudtrail.amazonaws.com"},
        "Action": "s3:GetBucketAcl",
        "Resource": f"arn:aws:s3:::{bucketName}"
      },
      {
        "Sid": "AWSCloudTrailWrite",
        "Effect": "Allow",
        "Principal": {"Service": "cloudtrail.amazonaws.com"},
        "Action": "s3:PutObject",
        "Resource": f"arn:aws:s3:::{bucketName}/AWSLogs/*/*",
        "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
      }
    ]
  }
  
  putPolicy = s3.put_bucket_policy(
    Bucket = bucketName,
    Policy = json.dumps(policy)
  )
  
  trailAccess = org.enable_aws_service_access(
    ServicePrincipal='cloudtrail.amazonaws.com'
  )

  create = trail.create_trail(
    Name = "organization-trail-DO-NOT-DELETE",
    S3BucketName = bucketName,
    IncludeGlobalServiceEvents = True,
    IsMultiRegionTrail = True,
    EnableLogFileValidation = True,
    IsOrganizationTrail = True
  )
  
  logging = trail.start_logging(
    Name = "organization-trail-DO-NOT-DELETE"
  )


def putEvent():
  metadata = {
    "metadata": {
      "service": "assembler-producer",
      "status": "SUCCEEDED"
    }
  }
  response = ebridge.put_events(
    Entries = [
      {
        'Source': 'assembler-producer',
        'DetailType': 'org-assemble event',
        'Detail': json.dumps(metadata) 
      }
    ]
  )

def handler(event, context):
    helper(event, context)