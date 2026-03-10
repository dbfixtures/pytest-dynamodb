# Copyright (C) 2025 by Authors.

# This file is part of pytest-dynamodb.

# pytest-dynamodb is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-dynamodb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-dynamodb. If not, see <http://www.gnu.org/licenses/>.
"""Pytester integration test for dynamodb fixture teardown."""

import uuid

import pytest
from mirakuru import TCPExecutor
from mypy_boto3_dynamodb import DynamoDBServiceResource
from pytest import MonkeyPatch, Pytester

pytest_plugins = ("pytester",)


def test_teardown_preserves_preexisting_tables_in_child_pytest_run(
    dynamodb: DynamoDBServiceResource,
    dynamodb_proc: TCPExecutor,
    pytester: Pytester,
    monkeypatch: MonkeyPatch,
) -> None:
    """Child pytest run should clean only its own tables."""
    suffix = uuid.uuid4().hex
    main_table = f"pytester_main_{suffix}"
    child_table = f"pytester_child_{suffix}"

    for index in range(110):
        dynamodb.create_table(
            TableName=f"pytester_preexisting_{index:03d}_{suffix}",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1,
            },
        )

    dynamodb.create_table(
        TableName=main_table,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1,
        },
    )

    monkeypatch.setenv("PYTESTER_MAIN_TABLE", main_table)
    monkeypatch.setenv("PYTESTER_CHILD_TABLE", child_table)
    pytester.copy_example("dynamodb_noproc/conftest.py")
    pytester.copy_example("dynamodb_noproc/test_child.py")

    result = pytester.runpytest_subprocess(
        "-q",
        # "-p",
        # "pytest_dynamodb.plugin",
        "--dynamodb-host",
        dynamodb_proc.host,
        "--dynamodb-port",
        str(dynamodb_proc.port),
    )
    result.assert_outcomes(passed=1)

    client = dynamodb.meta.client
    dynamodb.Table(main_table).wait_until_exists()
    dynamodb.Table(f"pytester_preexisting_109_{suffix}").wait_until_exists()
    with pytest.raises(client.exceptions.ResourceNotFoundException):
        client.describe_table(TableName=child_table)
