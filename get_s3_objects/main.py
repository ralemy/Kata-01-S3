from typing import List

import boto3
import botocore
import json

client = boto3.client('s3')


def get_bucket(event) -> str or None:
    if "queryStringParameters" not in event:
        return None
    if event["queryStringParameters"] is None:
        return None
    keys = [key for key in event["queryStringParameters"].keys() if key.lower() == 'bucket']
    if len(keys) == 0:
        return None
    return event["queryStringParameters"][keys[0]]


def check_bucket(bucket_name: str) -> int:
    try:
        s3 = boto3.resource('s3')
        s3.meta.client.head_bucket(Bucket=bucket_name)
        return 200
    except botocore.exceptions.ClientError as e:
        return int(e.response['Error']['Code'])


def respond(status: int, message: str or None, body: dict = None) -> dict:
    return {
        "statusCode": status,
        "body": json.dumps(body if body is not None else {"message": message})
    }


def list_objects(bucket_name: str) -> List[str]:
    return [f.key for f in boto3.resource('s3').Bucket(bucket_name).objects.all()]


def lambda_handler(event, _):
    bucket_name = get_bucket(event)

    if bucket_name is None:
        return respond(400, "no bucket specified")

    status = check_bucket(bucket_name)

    if status != 200:
        return respond(status, f"Failed to access bucket {bucket_name}. ({status})")

    objects = list_objects(bucket_name)

    return respond(200, None, {"objects": objects})
