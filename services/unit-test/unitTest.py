import json
import boto3


def checkPolicy(arn,bucket):
  iam = boto3.client('iam')

  iamResponse = iam.simulate_principal_policy(
    PolicySourceArn = arn,
    ActionNames =[
      's3:PutObject',
      's3:GetObject'
    ],
    ResourceArns = [
      'arn:aws:s3:::' + bucket + "/*"
    ]
  )['EvaluationResults']

  for result in iamResponse:
    print("%s - %s for %s" % (result['EvalActionName'], result['EvalDecision'], arn))


def checkTrail(accountTrail):
  trail = boto3.client('cloudtrail')
  
  trailResponse = trail.get_trail_status(
    Name=accountTrail
  )
  
  isLogging = trailResponse['IsLogging']

  trailEventResponse = trail.get_event_selectors(
    TrailName=accountTrail
  )
  
  trailEventTest = trailEventResponse['EventSelectors'][0]['DataResources'][0]['Values'][0]
  
  if(isLogging):
    print(accountTrail + " is actively logging, including data events for " + trailEventTest)
  else: 
    print(accountTrail + " is not logging")  
  

def checkBucket(bucket):
  s3 = boto3.client('s3')

  logResponse = s3.get_bucket_logging(
    Bucket=bucket
  )
  
  logTest = logResponse["LoggingEnabled"]["TargetBucket"]

  if(logTest == "264834854925-logs-do-not-delete"):
    print (bucket + " Log Success")
  else:
    print (bucket + " Log Failed!")
  
  encryptionResponse = s3.get_bucket_encryption(
    Bucket=bucket
  )
  
  encryptionTest = encryptionResponse["ServerSideEncryptionConfiguration"]["Rules"][0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']

  if(encryptionTest == "AES256"):
    print(bucket + " Encryption Success")
  else: 
    print(bucket + " Encryption Failed")

  

def lambda_handler(event, context):
  cf = boto3.client('cloudformation')

  output = cf.describe_stacks(
    StackName = 'green4'
  )

  logBucket= output['Stacks'][0]['Outputs'][3]['OutputValue']
  storageBucket = output['Stacks'][0]['Outputs'][0]['OutputValue']
  accountTrail = output['Stacks'][0]['Outputs'][2]['OutputValue']
  s3Role = output['Stacks'][0]['Outputs'][1]['OutputValue']
  
  
  checkBucket(logBucket)
  checkBucket(storageBucket)
  checkTrail(accountTrail)
  checkPolicy(s3Role,storageBucket)
