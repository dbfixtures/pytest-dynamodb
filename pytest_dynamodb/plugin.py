# Copyright (C) 2016 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-dynamodb.

# pytest-dbfixtures is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-dynamodb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-dynamodb.  If not, see <http://www.gnu.org/licenses/>.
"""Plugin module of pytest-dynamodb."""
from pytest import Parser

import pytest_dynamodb.factories.process
from pytest_dynamodb import factories

# pylint:disable=invalid-name
_help_dir = "Path to DynamoDB installation path"
_help_host = "Host at which DynamoDB will accept connections"
_help_port = "Port at which DynamoDB will accept connections"
_help_delay = "causes DynamoDB to introduce delays for certain operations"
_help_aws_secret_key = "AWS secret key."
_help_aws_access_key = "AWS access key."
_help_aws_region = "AWS region name."


def pytest_addoption(parser: Parser) -> None:
    """Configure options for pytest-dynamodb."""
    parser.addini(name="dynamodb_dir", help=_help_dir, default="/tmp/dynamodb")

    parser.addini(name="dynamodb_host", help=_help_host, default="127.0.0.1")

    parser.addini(
        name="dynamodb_port",
        help=_help_port,
        default=None,
    )

    parser.addini(name="dynamodb_delay", help=_help_delay, default=False)

    parser.addini(
        name="dynamodb_aws_secret_key",
        help=_help_aws_secret_key,
        default="fakeSecretAccessKey",
    )

    parser.addoption(
        "--dynamodb-aws_secret_key",
        action="store",
        dest="dynamodb_aws_secret_key",
        help=_help_aws_secret_key,
    )

    parser.addini(
        name="dynamodb_aws_access_key",
        help=_help_aws_access_key,
        default="fakeMyKeyId",
    )

    parser.addoption(
        "--dynamodb-aws_access_key",
        action="store",
        dest="dynamodb_aws_access_key",
        help=_help_aws_access_key,
    )

    parser.addini(
        name="dynamodb_aws_region",
        help=_help_aws_region,
        default="us-west-1",
    )

    parser.addoption(
        "--dynamodb-aws_region",
        action="store",
        dest="dynamodb_aws_region",
        help=_help_aws_region,
    )

    parser.addoption(
        "--dynamodb-dir",
        action="store",
        metavar="path",
        dest="dynamodb_dir",
        help=_help_dir,
    )

    parser.addoption(
        "--dynamodb-host",
        action="store",
        dest="dynamodb_host",
        help=_help_host,
    )

    parser.addoption(
        "--dynamodb-port", action="store", dest="dynamodb_port", help=_help_port
    )

    parser.addoption(
        "--dynamodb-delay",
        action="store",
        dest="dynamodb_delay",
        help=_help_delay,
    )


dynamodb_proc = pytest_dynamodb.factories.process.dynamodb_proc()
dynamodb_noproc = pytest_dynamodb.factories.noprocess.dynamodb_noproc()
dynamodb = factories.dynamodb("dynamodb_proc")
