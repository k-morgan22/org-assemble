import json
import boto3
from botocore.vendored import requests
import uuid


lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')



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
        
    except Exception as e:
        print("send response to cloudformation failed: " + str(e))


def deleteResponse(event, context):
    try:
        delete = lambdaClient.delete_function(
            FunctionName = event['ResourceProperties']['ServiceToken']
        )
        print("deleting lambda...")
        sendResponse(event, context, "SUCCESS", {})
    except ClientError as e:
        print(e)
        sendResponse(event, context, "FAILED", {})


def lambda_handler(event, context):
    lambdaArn = event['ResourceProperties']['ServiceToken']
    loggingEmail = event['ResourceProperties']['LoggingEmail']
    webhookUrl = event['ResourceProperties']['SlackWebHook']
    
    
    if(event['RequestType'] == 'Create'):
        try:

            randomName = 'slackDestinationsUrl-'+ str(uuid.uuid4())
            putParameter = ssm.put_parameter(
                Name = randomName,
                Description = 'Url for slack destinations reports',
                Value = webhookUrl,
                Type = 'SecureString'
            )

            initialQueue = sqs.get_queue_url(
                QueueName = ''
            )

            payload = { 'LoggingEmail': loggingEmail }
            
            batchResponse = sqs.send_message_batch(
                QueueUrl = initialQueue,
                Entries = [
                    {
                        'Id': '1',
                        'MessageBody': json.dumps(payload)
                    },
                    {
                        'Id': '2',
                        'MessageBody': json.dumps(payload)
                    }
                ]
            )

            sendResponse(event, context, "SUCCESS", {})
        except:
            print("failed to run program ")
            
            
    if(event['RequestType'] == 'Update'):
        try:
            sendResponse(event, context, "SUCCESS", {})
        except:
            print("Could not initiate update response")
    elif(event['RequestType'] == 'Delete'):
        try:
            deleteResponse(event, context)
        except:
            print("Could not initiate delete response")