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
"""Configuration tools for pytest-dynamodb."""

from pathlib import Path
from typing import Any, Optional, TypedDict

from _pytest.fixtures import FixtureRequest


class PytestDynamoDBConfigType(TypedDict):
    """Configuration type dict."""

    dir: Path
    host: str
    port: Optional[int]
    delay: bool
    aws_access_key: str
    aws_secret_key: str
    aws_region: str


def get_config(request: FixtureRequest) -> PytestDynamoDBConfigType:
    """Return a dictionary with config options."""

    def get_conf_option(option: str) -> Any:
        option_name = "dynamodb_" + option
        return request.config.getoption(option_name) or request.config.getini(
            option_name
        )

    port = None
    if get_conf_option("port"):
        port = int(get_conf_option("port"))

    config: PytestDynamoDBConfigType = {
        "dir": get_conf_option("dir"),
        "host": get_conf_option("host"),
        "port": port,
        "delay": bool(get_conf_option("delay")),
        "aws_access_key": get_conf_option("aws_access_key"),
        "aws_secret_key": get_conf_option("aws_secret_key"),
        "aws_region": get_conf_option("aws_region"),
    }
    return config
