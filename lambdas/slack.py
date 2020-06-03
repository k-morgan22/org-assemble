import json
import requests
import boto3

secret = boto3.client('secretsmanager')


def getUrl():
  urlResponse = secret.get_secret_value(
    SecretId = '/account-assemble/slack/slackUrl'
  )
  url = urlResponse['SecretString']
  return url

slackUrl = getUrl()

def formatSuccess(function):
  if function == "createOu":
    messageBody = "Workloads OU created"
  elif function == "createAccount":
    messageBody = "Account created"
  elif function == "logic":
    messageBody = "Your logic is correct!"
  elif function == "moveAccount":
    messageBody = "Account moved to Workloads OU"
  elif function == "stackset":
    messageBody = "Base account stackset deployed"
  elif function == "enableLogging":
    messageBody = "Data event logging enabled for account"
      
  format = {
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "SUCCESS :grin:\n" + messageBody
        }
      }
    ]
  }
  
  return format
  

def formatFailure(function, condition, errorType, message):
  format = {
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": ":warning: ERROR :warning:\n *Error Type:* " + errorType + " \n *Error Message:* " + message
        }
      },
      {
        "type": "context",
        "elements": [
          {
            "type": "mrkdwn",
            "text": "*Function:* " + function + " \n *Condition:* " + condition
          }
        ]
      }
    ]
  }
  return format

def lambda_handler(event, context):

  data = json.loads(event['Records'][0]['Sns']['Message'])
  status = data['requestContext']['condition'] 
  function = data['requestContext']['functionArn']

  # grab function name to customize slack success message
  start = 'function:'
  end = ':$LATEST'
  functionName = function[function.find(start)+len(start):function.rfind(end)]

  if(status == "Success"):
    message = formatSuccess(functionName)
  else:
    errorType = data['responsePayload']['errorType']
    errorMessage = data['responsePayload']['errorMessage']
    message = formatFailure(functionName, status, errorType, errorMessage)
  

  slackResponse = requests.post(
    slackUrl,
    json = message,
    headers = {'Content-Type': 'application/json'}
  )

  http_reply = {
    "statusCode": slackResponse.status_code,
    "body": slackResponse.text
  }

  return http_reply