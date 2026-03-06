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
from typing import Callable, Generator, Iterable

import pytest
from mirakuru import ProcessExitedWithError, TCPExecutor
from port_for import PortForException, PortType, get_port
from pytest import FixtureRequest, TempPathFactory

from pytest_dynamodb.config import DynamoDBConfig, get_config


class JarPathException(Exception):
    """Exception thrown, i ncase we can't locate dynamodb's dir to run dynamodb.

    We do not know where user has dynamodb jar file.
    So, we want to tell him that he has to provide a path to dynamodb dir.
    """

    def __init__(self, jar_path: str) -> None:
        """Initialize JarPathException exception."""
        super().__init__(
            f"Cannot find DynamoDBLocal.jar at: {jar_path}. "
            "Provide a valid path to the directory containing the jar."
        )


class DynamoDBPortUsedException(PortForException):
    """Exception thrown, in case only checked port can be found, but is taken."""

    def __init__(self, port: int) -> None:
        """Initialize DynamoDBNoFreePortException exception."""
        super().__init__(f"Port {port} already in use, probably by other instances of the test. ")


class DynamoDBNoFreePortException(PortForException):
    """Exception thrown, in case we can't find a free port."""

    def __init__(self, n: int, used_ports: Iterable[int]) -> None:
        """Initialize DynamoDBNoFreePortException exception."""
        super().__init__(
            f"Attempted {n} times to select ports. "
            f"All attempted ports: {', '.join(map(str, used_ports))} are already "
            f"in use, probably by other instances of the test."
        )


def _dynamodb_port(
    port: PortType | None, config: DynamoDBConfig, excluded_ports: Iterable[int]
) -> int:
    """User specified port, otherwise find an unused port from config."""
    dynamodb_port = get_port(port, excluded_ports) or get_port(config.port, excluded_ports)
    assert dynamodb_port is not None
    return dynamodb_port


def dynamodb_proc(
    dynamodb_dir: str | None = None,
    host: str | None = None,
    port: PortType | None = None,
    delay: bool = False,
) -> Callable[[FixtureRequest, TempPathFactory], Generator[TCPExecutor, None, None]]:
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
        tmp_path_factory: TempPathFactory,
    ) -> Generator[TCPExecutor, None, None]:
        """Process fixture for DynamoDB.

        It starts DynamoDB when first used and stops it at the end
        of the tests. Works on ``DynamoDBLocal.jar``.
        """
        config = get_config(request)
        path_dynamodb_jar = os.path.join((dynamodb_dir or config.dir), "DynamoDBLocal.jar")

        if not os.path.isfile(path_dynamodb_jar):
            raise JarPathException(path_dynamodb_jar)

        port_path = tmp_path_factory.getbasetemp()
        if hasattr(request.config, "workerinput"):
            port_path = tmp_path_factory.getbasetemp().parent

        n = 0
        used_ports: set[int] = set()
        while True:
            try:
                dynamodb_port = _dynamodb_port(port, config, used_ports)
                port_filename_path = port_path / f"dynamo-{dynamodb_port}.port"
                if dynamodb_port in used_ports:
                    raise DynamoDBPortUsedException(dynamodb_port)
                used_ports.add(dynamodb_port)
                with port_filename_path.open("x") as port_file:
                    port_file.write(f"dynamodb_port {dynamodb_port}\n")
                break
            except FileExistsError:
                n += 1
                if n >= config.port_search_count:
                    raise DynamoDBNoFreePortException(n, used_ports) from None
        assert dynamodb_port
        dynamodb_delay = "-delayTransientStatuses" if delay or config.delay else ""
        dynamodb_host = host if host is not None else config.host
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
