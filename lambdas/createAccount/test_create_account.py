from moto import mock_organizations
from moto import mock_ssm
from moto.organizations import utils
from unittest import TestCase
import boto3


class TestCreateAccount(TestCase):
  @mock_organizations
  def test_create_account(self):
    from createAccount import createAccount
    org = boto3.client('organizations')
    fakeOrg = org.create_organization(FeatureSet='ALL')

    result = createAccount("FakeEmail@gmail.com", "FakeName")
    self.assertIsNone(result)
    

  @mock_ssm
  def test_get_parameter(self):
    from createAccount import getEmail
    ssm = boto3.client('ssm')
    fakeParameter = ssm.put_parameter(
      Name = "Fake/emails/dev-123456789",
      Description = "Look at me, i'm a fake parameter!",
      Value = "FakeEmail@gmail.com",
      Type = 'String'
    )
    result = getEmail('Fake/emails', "dev")
    self.assertEqual(result, "FakeEmail@gmail.com")


