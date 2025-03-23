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
"""Tests main conftest file."""

from pytest_dynamodb import factories
from pytest_dynamodb.plugin import *  # noqa: F403

# pylint:disable=invalid-name
dynamodb_same = factories.dynamodb("dynamodb_proc")
dynamodb_diff = factories.dynamodb(
    "dynamodb_proc",
    access_key="fakeDeniedKeyId",
    secret_key="fakeDeniedSecretAccessKey",
)
# pylint:enable=invalid-name
