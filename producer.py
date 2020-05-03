import json
import boto3
from botocore.vendored import requests
from uuid import uuid4
import os


lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')
sns = boto3.client('sns')



def sendResponse(event, context, responseStatus, responseData = None):
  responseUrl = event['ResponseURL']
  print(responseUrl)

  responseBody = {}
  responseBody['Status'] = responseStatus
  responseBody['Reason'] = 'See print statements in console'
  responseBody['PhysicalResourceId'] = event['ResourceProperties']['ServiceToken']
  responseBody['StackId'] = event['StackId']
  responseBody['RequestId'] = event['RequestId']
  responseBody['LogicalResourceId'] = event['LogicalResourceId']
  responseBody['Data'] = responseData

  json_responseBody = json.dumps(responseBody)
  print("Response body:\n" + json_responseBody)

  try:
    response = requests.put(responseUrl,
                            data=json_responseBody)
    print("Status code: " + response.status)
      
  except:
    print("send response to cloudformation failed")


def deleteResponse(event, context):
  try:
    delete = lambdaClient.delete_function(
        FunctionName = event['ResourceProperties']['ServiceToken']
    )
    print("deleting lambda...")
    sendResponse(event, context, "SUCCESS", {})
  except:
    sendResponse(event, context, "FAILED", {})

def sendMessage(url, messageBody):
  response = sqs.send_message(
    QueueUrl = url,
    MessageBody = messageBody,
    MessageDeduplicationId= uuid4().hex,
    MessageGroupId='1'
  )


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
  lambdaArn = event['ResourceProperties']['ServiceToken']
  queueUrl = os.environ['NextQueue']
  topicArn = os.environ['SlackArn']
  
  
  if(event['RequestType'] == 'Create'):
    try:

      sendMessage(queueUrl, "create organizational units!")
    

      sendResponse(event, context, "SUCCESS", {})
    except:
      slackPublish(topicArn, "failed", "producer", None)
      sendResponse(event, context, "FAILED", {})
          
          
  if(event['RequestType'] == 'Update'):
    try:
      sendResponse(event, context, "SUCCESS", {})
    except:
      slackPublish(topicArn, "failed", "producer", None)
      sendResponse(event, context, "FAILED", {})      
  elif(event['RequestType'] == 'Delete'):
    try:
      deleteResponse(event, context)
    except:
      slackPublish(topicArn, "failed", "producer", None)
      sendResponse(event, context, "FAILED", {})