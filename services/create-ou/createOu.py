import json
import boto3
import uuid
import os

lambdaClient = boto3.client('lambda')
ssm = boto3.client('ssm')
sns = boto3.client('sns')


def invoke(funct):
  payload = {
    "origin": "createOu"
  }

  response = lambdaClient.invoke(
    FunctionName = funct,
    InvocationType = 'Event',
    LogType = 'None',
    Payload = json.dumps(payload)
  )



def slackPublish(arn, param1, param2, param3, status, function):
  payload = {
    "param1": param1, 
    "param2": param2,
    "param3": param3,
    "condition": status,
    "function": function
  }
  response = sns.publish(
    TopicArn = arn, 
    Message=json.dumps({'default': json.dumps(payload)}),
    MessageStructure='json'
  ) 



def lambda_handler(event, context):
  lambdaName = os.environ['LambdaName']
  topicArn = os.environ['SlackArn']
  nextFunct = os.environ['InvokeLambda']
  ouName = event['Records'][0]['body']


  try:
    
    masterId = 'r-0h4'
    ouId = 'o-' + str(uuid.uuid4())

    masterName = '/org-assemble/masterId/master-'+ str(uuid.uuid4())
    putParameter = ssm.put_parameter(
      Name = masterName,
      Description = 'Master Org Id',
      Value = masterId,
      Type = 'String'
    )

    if(ouName == 'Security'):
      securityName = '/org-assemble/ouId/security-'+ str(uuid.uuid4())
      putParameter = ssm.put_parameter(
        Name = securityName,
        Description = 'Security Ou Id',
        Value = ouId,
        Type = 'String'
      )
    else:
      workloadsName = '/org-assemble/ouId/workloads-'+ str(uuid.uuid4())
      putParameter = ssm.put_parameter(
        Name = workloadsName,
        Description = 'Workloads Ou Id',
        Value = ouId,
        Type = 'String'
      )

    invoke(nextFunct)
    slackPublish(topicArn, ouName, lambdaName, nextFunct, "success", lambdaName)
  except:
    slackPublish(topicArn, ouName, lambdaName, nextFunct, "failed", lambdaName)
    