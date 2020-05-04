import json
import boto3
# from botocore.vendored import requests
import urllib.request

secret = boto3.client('secretsmanager')

def getUrl():
  urlResponse = secret.get_secret_value(
    SecretId = '/org-assemble/slack/slackUrl'
  )
  url = urlResponse['SecretString']
  return url
  

def lambda_handler(event, context):
  messageBody = json.loads(event['Records'][0]['Sns']['Message'])
  
  
  if(messageBody['condition'] == "success"):
    data = {
      "blocks": [
    		{
    			"type": "section",
    			"text": {
    				"type": "mrkdwn",
    				"text": "SUCCESS :grin:\n" + messageBody['text']
    			}
    		}
    	]
    }
  else:
    data = {
      "blocks": [
    		{
    			"type": "section",
    			"text": {
    				"type": "mrkdwn",
    				"text": ":warning: ERROR :warning:\nSomething went wrong, organization could not be created!"
    			}
    		},
    		{
    			"type": "context",
    			"elements": [
    				{
    					"type": "mrkdwn",
    					"text": "*Function:* " + messageBody['function']
    				}
    			]
    		}
    	]
    }
    
  
  slackUrl = getUrl()

  
  # slackResponse = requests.post(
  #   slackUrl,
  #   json = data,
  #   headers = {'Content-Type': 'application/json'}
  # )
  
  request = urllib.request.Request(
    slackUrl, 
    data=json.dumps(data).encode("utf-8"), 
    method="POST"
  )
  
  with urllib.request.urlopen(request) as response:
    response_body = response.read().decode("utf-8")
  
  http_reply = {
    "statusCode": 200,
    "body": response_body
  }

  return http_reply

  