import json
import boto3
from botocore.vendored import requests
import uuid
import os


lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
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

def messageFormat(body):
  message = {
    'id': uuid4().hex,
    'string': body
  }
  return message 

def sendMessage(url, body_list):
  messages_list = [messageFormat(each) for each in body_list]
  
  response = sqs.send_message_batch(
    QueueUrl = url,
    Entries = [{'Id': message['id'], 'MessageBody': message['string'],'MessageDeduplicationId': message['id'],'MessageGroupId': '1'} for message in messages_list]
  )

def slackPublish(arn, param1, param2, param3, status):
  payload = {
    "param1": param1, 
    "param2": param2,
    "param3": param3,
    "condition": status
  }
  response = sns.publish(
    TopicArn = arn, 
    Message=json.dumps({'default': json.dumps(payload)}),
    MessageStructure='json'
  ) 




def lambda_handler(event, context):
  lambdaArn = event['ResourceProperties']['ServiceToken']
  webhookUrl = os.environ['SlackWebHook']
  queueUrl = os.environ['NextQueue']
  topicArn = os.environ['SlackArn']
  
  
  if(event['RequestType'] == 'Create'):
    try:
      randomName = '/org-assemble/slack/slackUrl-'+ str(uuid.uuid4())
      putParameter = ssm.put_parameter(
        Name = randomName,
        Description = 'Url for slack reports',
        Value = webhookUrl,
        Type = 'SecureString'
      )

      ouNames = ["Security", "Workloads"]
      sendMessage(queueUrl, ouNames)
    
      slackPublish(topicArn, queueUrl, webhookUrl, topicArn, "success")

      sendResponse(event, context, "SUCCESS", {})
    except:
      slackPublish(topicArn, queueUrl, webhookUrl, topicArn, "failed")
          
          
  if(event['RequestType'] == 'Update'):
    try:
      sendResponse(event, context, "SUCCESS", {})
    except:
      slackPublish(topicArn, queueUrl, webhookUrl, topicArn, "failed update")
  elif(event['RequestType'] == 'Delete'):
    try:
      deleteResponse(event, context)
    except:
      slackPublish(topicArn, queueUrl, webhookUrl, topicArn, "failed delete")