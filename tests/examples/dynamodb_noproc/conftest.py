"""Set of tests to test table cleanup."""

from pytest_dynamodb import factories

dynamodb = factories.dynamodb("dynamodb_noproc")
