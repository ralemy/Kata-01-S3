import boto3
import os
from pathlib import Path

TEST_BUCKET = "some_bucket"
FILE_LIST = ['buck1.csv', 'buck2.csv', 'some_file.csv']
FIXTURES = os.path.join(os.path.dirname(__file__), "unit", "fixtures")


def upload_fixtures(bucket: str, fixtures: str) -> None:
    client = boto3.client("s3")
    fixture_paths = [os.path.join(p, f) for p, _, files in os.walk(fixtures) for f in files]
    for path in fixture_paths:
        client.upload_file(Filename=path, Bucket=bucket, Key=os.path.relpath(path, fixtures))


def create_s3_files(fixtures: str) -> None:
    [Path(os.path.join(fixtures, name)).touch() for name in FILE_LIST]


def delete_s3_files(fixtures: str) -> None:
    [os.remove(os.path.join(fixtures, file)) for file in FILE_LIST]
