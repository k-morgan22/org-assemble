import json
import boto3
import os

# lambdaClient = boto3.client('lambda')
ssm = boto3.client('ssm')
sns = boto3.client('sns')


def getLogBucket(path, decryption):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = decryption
  )
  
  for param in response['Parameters']:
    if 'cloudtrail' in param['Name']:
      return param['Value']


def getEnvBuckets(path, decryption):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = decryption
  )
  
  buckets = []
  
  for param in response['Parameters']:
    buckets.append(param['Value'])
  
  return buckets
  
 
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
    logBucket = getLogBucket('/org-assemble/logAccountBucket', False)
    bucketList = getEnvBuckets('/org-assemble/envAccountBucket', False)
    
    
    slackPublish(topicArn, "success", None, "Finished assembling your AWS organization")
  except:
    slackPublish(topicArn, "failed", lambdaName, None)