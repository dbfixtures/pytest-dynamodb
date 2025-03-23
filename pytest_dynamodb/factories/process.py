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
"""Process fixture factory."""

import os
from typing import Any, Callable, Generator, Optional

import pytest
from _pytest.fixtures import FixtureRequest
from mirakuru import ProcessExitedWithError, TCPExecutor
from port_for import PortType, get_port

from pytest_dynamodb.config import get_config


class JarPathException(Exception):
    """Exception thrown, i ncase we can't locate dynamodb's dir to run dynamodb.

    We do not know where user has dynamodb jar file.
    So, we want to tell him that he has to provide a path to dynamodb dir.
    """


def dynamodb_proc(
    dynamodb_dir: Optional[str] = None,
    host: str = "localhost",
    port: Optional[PortType] = None,
    delay: bool = False,
) -> Callable[[FixtureRequest], Any]:
    """Process fixture factory for DynamoDB.

    :param str dynamodb_dir: a path to dynamodb dir (without spaces)
    :param str host: hostname
    :param int port: port
    :param bool delay: causes DynamoDB to introduce delays for certain
        operations

    .. note::
        For more information visit:
            http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html

    :return: function which makes a DynamoDB process
    """

    @pytest.fixture(scope="session")
    def dynamodb_proc_fixture(
        request: FixtureRequest,
    ) -> Generator[TCPExecutor, None, None]:
        """Process fixture for DynamoDB.

        It starts DynamoDB when first used and stops it at the end
        of the tests. Works on ``DynamoDBLocal.jar``.

        :param FixtureRequest request: fixture request object
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor
        """
        config = get_config(request)
        path_dynamodb_jar = os.path.join(
            (dynamodb_dir or config["dir"]), "DynamoDBLocal.jar"
        )

        if not os.path.isfile(path_dynamodb_jar):
            raise JarPathException(
                "You have to provide a path to the dir with dynamodb jar file."
            )

        dynamodb_port = get_port(port or config["port"])
        assert dynamodb_port
        dynamodb_delay = (
            "-delayTransientStatuses" if delay or config["delay"] else ""
        )
        dynamodb_host = host or config["host"]
        dynamodb_executor = TCPExecutor(
            f"java -Djava.library.path=./DynamoDBLocal_lib "
            f"-jar {path_dynamodb_jar} "
            f"-inMemory {dynamodb_delay} "
            f"-port {dynamodb_port}",
            host=dynamodb_host,
            port=dynamodb_port,
            timeout=60,
        )
        dynamodb_executor.start()
        yield dynamodb_executor
        try:
            dynamodb_executor.stop()
        except ProcessExitedWithError:
            pass

    return dynamodb_proc_fixture
