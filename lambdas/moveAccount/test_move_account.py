from moto import mock_organizations
from moto import mock_ssm
from moto.organizations import utils
from unittest import TestCase
import boto3


class TestMoveAccount(TestCase):
  @mock_organizations
  def test_name(self):
    from moveAccount import grabName
    org = boto3.client('organizations')
    fakeOrg = org.create_organization(FeatureSet='ALL')
    fakeAccountId = org.create_account(
      Email="FakeEmail@gmail.com",
      AccountName="Prod",
      RoleName='OrganizationRole',
      IamUserAccessToBilling='DENY'
    )['CreateAccountStatus']['AccountId']

    result = grabName(fakeAccountId)
    self.assertEqual(result, "Prod")


  @mock_organizations
  def test_create_ou(self):
    from moveAccount import moveAccount
    org = boto3.client('organizations')
    fakeOrg = org.create_organization(FeatureSet='ALL')
    rootId = org.list_roots()['Roots'][0]['Id']
    ouId = org.create_organizational_unit(
      ParentId = rootId,
      Name = "Logging"
    )['OrganizationalUnit']['Id']
    fakeAccountId = org.create_account(
      Email="ReallyFakeEmail@gmail.com",
      AccountName="LogAccount",
      RoleName='OrganizationRole',
      IamUserAccessToBilling='DENY'
    )['CreateAccountStatus']['AccountId']

    result = moveAccount(fakeAccountId, rootId, ouId)
    self.assertIsNone(result)


  @mock_ssm
  def test_grab_three_parameters(self):
    from moveAccount import getOrgIds
    ssm = boto3.client('ssm')
    fakeParameter1 = ssm.put_parameter(
      Name = "Fake/ids/master-123456789",
      Description = "Look at me, i'm a fake parameter!",
      Value = "ou-42to-rgln9eje",
      Type = 'String'
    )
    fakeParameter2 = ssm.put_parameter(
      Name = "Fake/ids/security-987654321",
      Description = "Another One!",
      Value = "ou-42to-2eqoc4xf",
      Type = 'String'
    )
    fakeParameter3 = ssm.put_parameter(
      Name = "Fake/ids/workloads-135792468",
      Description = "One more time!",
      Value = "ou-42to-pb92rwtj",
      Type = 'String'
    )

    result = getOrgIds("Fake/ids", False)
    self.assertTupleEqual(result, ('ou-42to-rgln9eje', 'ou-42to-2eqoc4xf', 'ou-42to-pb92rwtj'))


  #test lambda accidental trigger
