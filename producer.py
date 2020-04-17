import json
import boto3
from botocore.vendored import requests


lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')



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
    
    
    if(event['RequestType'] == 'Create'):
        try:
            initialQueue = sqs.get_queue_url(
                QueueName = ''
            )

            payload = { 'LoggingEmail': loggingEmail }
            
            batchResponse = sqs.send_message_batch(
                QueueUrl = initialQueue,
                Entries = [
                    {
                        'Id': '1',
                        'MessageBody': JSON.stringify(payload)
                    },
                    {
                        'Id': '2',
                        'MessageBody': JSON.stringify(payload)
                    }
                ]
            )

            sendResponse(event, context, "SUCCESS", {})
        except:
            print("failed")
            
            
    if(event['RequestType'] == 'Update'):
        sendResponse(event, context, "SUCCESS", {})
    elif(event['RequestType'] == 'Delete'):
        try:
            deleteResponse(event, context)
        except:
            print("Could not initiate delete response")