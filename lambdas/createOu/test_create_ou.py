from moto import mock_organizations
from moto import mock_ssm
from moto.organizations import utils
from unittest import TestCase
import boto3


class TestCreateOu(TestCase):
  @mock_organizations
  def test_master_id(self):
    from createOu import grabMasterId
    org = boto3.client('organizations')
    fakeOrg = org.create_organization(FeatureSet='ALL')

    results = grabMasterId()
    self.assertRegex(results, utils.ROOT_ID_REGEX)

  @mock_organizations
  def test_create_ou(self):
    from createOu import createOrgUnit
    org = boto3.client('organizations')
    fakeOrg = org.create_organization(FeatureSet='ALL')
    rootId = org.list_roots()['Roots'][0]['Id']

    result = createOrgUnit(rootId, "Security")
    self.assertRegex(result, utils.OU_ID_REGEX)

  @mock_ssm
  @mock_organizations
  def test_put_parameter(self):
    from createOu import putParameter 
    org = boto3.client('organizations')
    ssm = boto3.client('ssm')
    fakeOrg = org.create_organization(FeatureSet='ALL')
    rootId = org.list_roots()['Roots'][0]['Id']

    result = putParameter('/random/stored/data-', 'Random stored data', rootId)
    self.assertIsNone(result)
