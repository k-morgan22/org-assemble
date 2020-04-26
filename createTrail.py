import json
import boto3
import uuid
from uuid import uuid4
import os

lambdaClient = boto3.client('lambda')
sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
sns = boto3.client('sns')


# def getBucketArns():
#   devFilterResponse = ssm.describe_parameters(
#     ParameterFilters = [
#       {
#         'Key':'Name' ,
#         'Option':'BeginsWith',
#         'Values': [
#           '/org-assemble/ouId/security-'
#         ]
#       },
#     ],
#     MaxResults = 1
#   )
  
#   devParamName = devFilterResponse['Parameters'][0]['Name']
  
#   devFilteredParam = ssm.get_parameter(
#     Name = devParamName
#   )
#   devParam = devFilteredParam['Parameter']['Value']

#   stagingFilterResponse = ssm.describe_parameters(
#     ParameterFilters = [
#       {
#         'Key':'Name' ,
#         'Option':'BeginsWith',
#         'Values': [
#           '/org-assemble/ouId/workloads-'
#         ]
#       },
#     ],
#     MaxResults = 1
#   )
  
#   stagingParamName = stagingFilterResponse['Parameters'][0]['Name']
  
#   stagingFilteredParam = ssm.get_parameter(
#     Name = stagingParamName
#   )
#   stagingParam = stagingFilteredParam['Parameter']['Value']

#   prodFilterResponse = ssm.describe_parameters(
#     ParameterFilters = [
#       {
#         'Key':'Name' ,
#         'Option':'BeginsWith',
#         'Values': [
#           '/org-assemble/ouId/workloads-'
#         ]
#       },
#     ],
#     MaxResults = 1
#   )
  
#   prodParamName = prodFilterResponse['Parameters'][0]['Name']
  
#   prodFilteredParam = ssm.get_parameter(
#     Name = prodParamName
#   )
#   prodParam = prodFilteredParam['Parameter']['Value']

#   logFilterResponse = ssm.describe_parameters(
#     ParameterFilters = [
#       {
#         'Key':'Name' ,
#         'Option':'BeginsWith',
#         'Values': [
#           '/org-assemble/ouId/workloads-'
#         ]
#       },
#     ],
#     MaxResults = 1
#   )
  
#   logParamName = logFilterResponse['Parameters'][0]['Name']
  
#   logFilteredParam = ssm.get_parameter(
#     Name = logParamName
#   )
#   logParam = logFilteredParam['Parameter']['Value']
#   return devParam, stagingParam, prodParam, logParam



def slackPublish(arn, status, function):
  payload = {
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


  try:
    # [devBucket, stagingBucket, prodBucket, logBucket] = getBucketArns()

    slackPublish(topicArn, "success", lambdaName)
  except:
    slackPublish(topicArn, "failed", lambdaName)