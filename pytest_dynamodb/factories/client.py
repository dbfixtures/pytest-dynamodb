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
"""Client fixture factory."""
from typing import Any, Callable, Generator, Optional, Union

import boto3
import pytest
from mirakuru import TCPExecutor
from mypy_boto3_dynamodb import DynamoDBServiceResource
from pytest import FixtureRequest

from pytest_dynamodb.config import get_config
from pytest_dynamodb.factories.noprocess import NoProcExecutor


def dynamodb(
    process_fixture_name: str,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    region: Optional[str] = None,
) -> Callable[[FixtureRequest], Any]:
    """Fixture factory for DynamoDB resource.

    :param str process_fixture_name: name of the process fixture
    :param str access_key: AWS acccess key
    :param str secret_key: AWS secret key
    :param str region: AWS region name
    :rtype: func
    :returns: function which makes a connection to DynamoDB
    """

    @pytest.fixture
    def dynamodb_factory(
        request: FixtureRequest,
    ) -> Generator[DynamoDBServiceResource, None, None]:
        """Fixture for DynamoDB resource.

        :param FixtureRequest request: fixture request object
        :rtype: Subclass of :py:class:`~boto3.resources.base.ServiceResource`
            https://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html#DynamoDB.Client
        :returns: connection to DynamoDB database
        """
        proc_fixture: Union[TCPExecutor, NoProcExecutor] = (
            request.getfixturevalue(process_fixture_name)
        )
        config = get_config(request)

        dynamo_db = boto3.resource(
            "dynamodb",
            endpoint_url=f"http://{proc_fixture.host}:{proc_fixture.port}",
            aws_access_key_id=access_key or config["aws_access_key"],
            aws_secret_access_key=secret_key or config["aws_secret_key"],
            region_name=region or config["aws_region"],
        )
        pre_existing_tables = dynamo_db.meta.client.list_tables()
        yield dynamo_db
        for table in dynamo_db.tables.all():  # pylint:disable=no-member
            if table.table_name not in pre_existing_tables:
                table.delete()

    return dynamodb_factory
