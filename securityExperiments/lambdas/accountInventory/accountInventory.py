import boto3
# import pandas as pd
from datetime import datetime
from io import StringIO
import logging

org = boto3.client('organizations')
s3 = boto3.resource('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def grabAccounts():
  
  accountList = []

  response = org.list_accounts()

  for account in response['Accounts']:
    accountDict = {
      'Name': account['Name'],
      'Id': account['Id'],
      'Email': account['Email']
    }
    accountList.append(accountDict)

    if account['Name'] == 'Logging':
      loggingAccount = account['Id']
    
  return accountList, loggingAccount
    

def sendReport(content, accountNum):
  BUCKET_NAME = 'security-reports-' + accountNum
  PREFIX = 'inventory-reports/'
  
  now = datetime.now()
  FILENAME = PREFIX + now.strftime("%m-%d-%Y_%H:%M:%S")
  
  
  s3.Object(BUCKET_NAME, FILENAME).put(Body = content.getvalue())  
  logger.info("Sent report to s3") 




def lambda_handler(event, context):
  accountList, loggingAccount = grabAccounts()
  logger.info("Grabbed all account information from organization") 
  
  df = pd.DataFrame(accountList)
  fileBuffer = StringIO()
  df.to_string(fileBuffer, index=False)  
  logger.info("Created dataframe") 
  
  sendReport(fileBuffer, loggingAccount)


