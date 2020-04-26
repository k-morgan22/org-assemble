import json
import boto3
from botocore.vendored import requests

ssm = boto3.client('ssm')

def getUrl():
  ssmFilterResponse = ssm.describe_parameters(
    ParameterFilters = [
      {
        'Key':'Name' ,
        'Option':'BeginsWith',
        'Values': [
          value
        ]
      },
    ],
    MaxResults = 1
  )
  
  webhookName = ssmFilterResponse['Parameters'][0]['Name']
  print(webhookName)
  
  urlResponse = ssm.get_parameter(
    Name = webhookName,
    WithDecryption = True
  )
  url = urlResponse['Parameter']['Value']
  return url
  

def lambda_handler(event, context):
  messageBody = json.loads(event['Records'][0]['Sns']['Message'])
  
  # function = messageBody['functionArn']
  # condition = messageBody['condition']
  # data = {
  #   "Function": function,
  #   "Condition": condition
  # }

  # message = json.dumps(data)
  message = json.dumps(messageBody)

  
  slackUrl = getUrl()
  
  
  slackResponse = requests.post(
    slackUrl,
    json = {"text": message},
    headers = {'Content-Type': 'application/json'}
  )
  
  http_reply = {
    "statusCode": 200,
    "body": slackResponse.text
  }

  print(message)
  return http_reply
  