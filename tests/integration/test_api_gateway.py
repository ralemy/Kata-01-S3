import os
from typing import cast
from unittest import TestCase

import boto3
import botocore
import requests
from mypy_boto3_s3.type_defs import CreateBucketConfigurationTypeDef

from tests.utils import create_s3_files, upload_fixtures, FIXTURES, delete_s3_files, FILE_LIST

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""


class TestApiGateway(TestCase):
    api_endpoint: str

    @classmethod
    def get_stack_name(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name where we are running integration tests."
            )

        return stack_name

    @classmethod
    def get_bucket_name(cls) -> str:
        bucket_name = os.environ.get("BUCKET_NAME")
        if not bucket_name:
            raise Exception(
                "Cannot find env var BUCKET_NAME. \n"
                "Please setup this environment variable with the bucket name where we are running integration tests."
            )

        return bucket_name

    @classmethod
    def setUpClass(cls) -> None:
        TestApiGateway.setup_bucket()

    @classmethod
    def tearDownClass(cls) -> None:
        bucket = boto3.resource('s3').Bucket(TestApiGateway.get_bucket_name())
        for obj in bucket.objects.all():
            obj.delete()
        bucket.delete()
        delete_s3_files(FIXTURES)

    def setUp(self) -> None:
        """
        Based on the provided env variable AWS_SAM_STACK_NAME,
        here we use cloudformation API to find out what the HelloWorldApi URL is
        """
        stack_name = TestApiGateway.get_stack_name()

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        stacks = response["Stacks"]

        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "GetS3ObjectsAPI"]
        self.assertTrue(api_outputs, f"Cannot find output GetS3ObjectsAPI in stack {stack_name}")

        self.api_endpoint = api_outputs[0]["OutputValue"]

    @classmethod
    def setup_bucket(cls):
        bucket = TestApiGateway.get_bucket_name()
        try:
            s3 = boto3.resource('s3')
            s3.meta.client.head_bucket(Bucket=bucket)
        except botocore.exceptions.ClientError:
            pass
        else:
            raise Exception(
                f"Test Bucket {bucket} already exists. please delete before proceeding."
            )

        config = cast(CreateBucketConfigurationTypeDef, {'LocationConstraint': 'us-west-2'})
        boto3.client('s3').create_bucket(Bucket=bucket, CreateBucketConfiguration=config)
        create_s3_files(FIXTURES)
        upload_fixtures(bucket, FIXTURES)

    def tearDown(self) -> None:
        pass

    def test_api_gateway_will_fail_with_no_params(self):
        """
        Call the API Gateway endpoint and check the response
        """
        response = requests.get(self.api_endpoint)
        self.assertDictEqual(response.json(), {"message": "no bucket specified"})
        self.assertEqual(response.status_code, 400)

    def test_api_gateway_will_fail_with_no_bucket(self):
        """
        Call the API Gateway endpoint and check the response
        """
        response = requests.get(self.api_endpoint + '?some_key=some_value')
        self.assertDictEqual(response.json(), {"message": "no bucket specified"})
        self.assertEqual(response.status_code, 400)

    def test_api_gateway_will_fail_with_non_existent_bucket(self):
        """
        Call the API Gateway endpoint and check the response
        """
        response = requests.get(self.api_endpoint + '?Bucket=some_value')
        self.assertDictEqual(response.json(), {"message": 'Failed to access bucket some_value. (404)'})
        self.assertEqual(response.status_code, 404)

    def test_api_gateway_will_pass(self):
        response = requests.get(self.api_endpoint + '?Bucket=' + self.get_bucket_name())
        self.assertDictEqual(response.json(), {"objects": FILE_LIST})
        self.assertEqual(response.status_code, 200)
