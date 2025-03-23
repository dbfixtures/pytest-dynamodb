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
"""No process fixture factory."""
from typing import Any, Callable, Generator, NamedTuple, Optional

import pytest
from pytest import FixtureRequest

from pytest_dynamodb.config import get_config


class NoProcExecutor(NamedTuple):
    """Fake executor."""

    host: str
    port: int


def dynamodb_noproc(
    host: Optional[str] = None,
    port: Optional[int] = None,
) -> Callable[[FixtureRequest], Any]:
    """Process fixture factory for DynamoDB.

    :param str host: hostname
    :param int port: port

    .. note::

        For more information visit:
            http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html

    :return: function which makes a DynamoDB process
    """

    @pytest.fixture(scope="session")
    def dynamodb_noproc_fixture(
        request: FixtureRequest,
    ) -> Generator[NoProcExecutor, None, None]:
        """Process fixture for DynamoDB.

        It starts DynamoDB when first used and stops it at the end
        of the tests. Works on ``DynamoDBLocal.jar``.

        :param FixtureRequest request: fixture request object
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor
        """
        config = get_config(request)

        dynamodb_port = port or config["port"] or 8000
        dynamodb_host = host or config["host"]

        noop_exec = NoProcExecutor(dynamodb_host, dynamodb_port)

        yield noop_exec

    return dynamodb_noproc_fixture
