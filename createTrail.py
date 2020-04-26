import boto3


org = boto3.client('organizations')
trail = boto3.client('cloudtrail')


def lambda_handler(event, context):
  trailAccess = org.enable_aws_service_access(
    ServicePrincipal='cloudtrail.amazonaws.com'
  )
  
  response = trail.create_trail(
    Name = 'trailName',
    S3BucketName = 'bucketArn',
    IncludeGlobalServiceEvents = True,
    IsMultiRegionTrail = True,
    EnableLogFileValidation = True,
    IsOrganizationTrail = True
  )
  
  startLogging = trail.start_logging(
    Name = 'trailName'
  )
  
  
  addEvents = trail.put_event_selectors(
    TrailName = 'trailName',
    EventSelectors = [
      {
        'DataResources': [
          {
            'Type': 'AWS::S3::Object',
            'Values': [
              'accountS3Arn/',
              'accountS3Arn/'
            ]
          }
        ]
      }
    ]
  )
  