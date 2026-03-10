"""Set of tests to test table cleanup."""

import os

from mypy_boto3_dynamodb import DynamoDBServiceResource


def test_child_table_cleanup(dynamodb: DynamoDBServiceResource) -> None:
    """Child table should be removed after test run."""
    main_table = os.environ["PYTESTER_MAIN_TABLE"]
    child_table = os.environ["PYTESTER_CHILD_TABLE"]

    dynamodb.create_table(
        TableName=child_table,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1,
        },
    )

    names = set(dynamodb.meta.client.list_tables()["TableNames"])
    assert main_table in names
    assert child_table in names
