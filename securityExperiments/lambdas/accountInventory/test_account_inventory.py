from moto import mock_organizations
from moto import mock_s3
from moto.organizations import utils
from unittest import TestCase
from unittest.mock import patch
import boto3
from io import StringIO


class TestAccountInventory(TestCase):
  @mock_organizations
  def test_name(self):
    from accountInventory import grabAccounts
    org = boto3.client('organizations')
    fakeOrg = org.create_organization(FeatureSet='ALL')
    fakeNames = ['Logging', 'Dev', 'Staging','Prod', 'OrgMaster']
    for name in fakeNames:
      email = 'FakeEmail+' + name + '@gmail.com'
      fakeAccount = org.create_account(
        Email= email,
        AccountName= name,
        RoleName='OrganizationRole',
        IamUserAccessToBilling='DENY'
      )

    result = grabAccounts()
    expected = ([{},{},{},{},{}],'')
    self.assertEqual(type(result), type(expected))
    

  @mock_s3
  def test_send_report(self):
    from accountInventory import sendReport
    s3 = boto3.resource('s3')
    fakeBucket = s3.create_bucket(Bucket="security-reports-123456789")
    with patch('sys.stdout', new=StringIO()) as fakeContent:
      result = sendReport(fakeContent, "123456789")
    self.assertIsNone(result)
    