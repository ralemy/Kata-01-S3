import json
import unittest
import mock
from typing import cast

import botocore
import boto3
import moto

from tests.utils import TEST_BUCKET, FILE_LIST, FIXTURES, upload_fixtures, create_s3_files, delete_s3_files

from mypy_boto3_s3 import S3Client, S3ServiceResource
from mypy_boto3_s3.type_defs import CreateBucketConfigurationTypeDef

with moto.mock_s3():
    from get_s3_objects import main


@moto.mock_s3
class TestGetS3Buckets(unittest.TestCase):

    @staticmethod
    def create_client() -> S3Client:
        return boto3.client("s3", region_name="us-east-2",
                            aws_access_key_id="some_access_key",
                            aws_secret_access_key="some_secret_key")

    @staticmethod
    def create_resource() -> S3ServiceResource:
        return boto3.resource("s3", region_name="us-east-2",
                              aws_access_key_id="some_access_key",
                              aws_secret_access_key="some_secret_key")

    def setUp(self) -> None:
        client = self.create_client()
        try:
            s3 = self.create_resource()
            s3.meta.client.head_bucket(Bucket=TEST_BUCKET)
        except botocore.exceptions.ClientError:
            pass
        else:
            err = "{bucket} should not exist".format(bucket=TEST_BUCKET)
            raise EnvironmentError(err)
        client.create_bucket(Bucket=TEST_BUCKET,
                             CreateBucketConfiguration=cast(CreateBucketConfigurationTypeDef,
                                                            {'LocationConstraint': 'us-east-2'}))
        create_s3_files(FIXTURES)
        upload_fixtures(TEST_BUCKET, FIXTURES)

    def tearDown(self) -> None:
        bucket = self.create_resource().Bucket(TEST_BUCKET)
        for obj in bucket.objects.all():
            obj.delete()
        bucket.delete()
        delete_s3_files(FIXTURES)

    def test_get_s3_resource(self):
        event = {}
        with mock.patch('get_s3_objects.main.get_bucket',
                        side_effect=['some_bucket', None, 'some_bucket', 'some_bucket']) as get_bucket:
            with mock.patch('get_s3_objects.main.check_bucket', side_effect=[200, 403, 404]) as check_bucket:
                resp1 = main.lambda_handler(event, '')
                resp2 = main.lambda_handler(event, '')
                resp3 = main.lambda_handler(event, '')
                resp4 = main.lambda_handler(event, '')
        get_bucket.assert_called_with(event)
        check_bucket.assert_called_with('some_bucket')
        self.assertEqual(resp1["statusCode"], 200)
        self.assertEqual(resp2["statusCode"], 400)
        self.assertEqual(resp3["statusCode"], 403)
        self.assertEqual(resp4["statusCode"], 404)

    def test_get_bucket_param_no_key(self):
        event = {}
        assert main.get_bucket(event) is None

    def test_get_bucket_param_no_parameters(self):
        event = {'queryStringParameters': None}
        assert main.get_bucket(event) is None

    def test_get_bucket_param_no_bucket(self):
        event = {'queryStringParameters': {'some_key': 'some_value'}}
        assert main.get_bucket(event) is None

    def test_get_bucket_param_with_bucket(self):
        event = {'queryStringParameters': {'bucKet': 'some_value'}}
        self.assertEqual(main.get_bucket(event), 'some_value')

    def test_check_bucket_with_404(self):
        resp = main.check_bucket('non_existent_bucket')
        self.assertEqual(resp, 404)

    def test_check_bucket_with_200(self):
        resp = main.check_bucket(TEST_BUCKET)
        self.assertEqual(resp, 200)

    def test_check_bucket_with_403(self):
        exception = botocore.exceptions.ClientError({"Error": {"Code": 403}}, 'open')
        mocked_s3 = mock.MagicMock()
        mocked_s3.meta = mock.Mock()
        mocked_s3.meta.client = mock.Mock()
        mocked_s3.meta.client.head_bucket = mock.Mock()
        mocked_s3.meta.client.head_bucket.side_effect = exception
        with mock.patch('boto3.resource', return_value=mocked_s3) as mocked_resource:
            resp = main.check_bucket(TEST_BUCKET)
        mocked_resource.assert_called_with('s3')
        mocked_s3.meta.client.head_bucket.assert_called_with(Bucket=TEST_BUCKET)
        self.assertEqual(resp, 403)

    def test_respond_without_body(self):
        resp = main.respond(500, 'some message')
        self.assertDictEqual({"statusCode": 500, "body": json.dumps({"message": "some message"})}, resp)

    def test_respond_with_body(self):
        resp = main.respond(500, None, {"some_key": 'some message'})
        self.assertDictEqual({"statusCode": 500, "body": json.dumps({"some_key": "some message"})}, resp)

    def test_list_objects(self):
        resp = main.list_objects(TEST_BUCKET)
        self.assertEqual(resp, FILE_LIST)


if __name__ == "__main__":
    unittest.main()
