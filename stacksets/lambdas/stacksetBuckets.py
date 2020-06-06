from crhelper import CfnResource
import boto3


helper = CfnResource()
s3 = boto3.resource('s3')


@helper.create
@helper.update
def no_op(_, __):
    pass

@helper.delete
def delete(event, context):
  accountId = event['ResourceProperties']['accountId']
  storageBucketName = event['ResourceProperties']['storageBucket']
  logBucketName = event['ResourceProperties']['logBucket']
  emptyList = [storageBucketName, logBucketName]

  for bucketName in emptyList:
    bucket = s3.Bucket(bucketName)
    bucket.objects.delete()


def handler(event, context):
    helper(event, context)