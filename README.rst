.. image:: https://raw.githubusercontent.com/dbfixtures/pytest-dynamodb/master/logo.png
    :width: 100px
    :height: 100px

pytest-dynamodb
===============

.. image:: https://img.shields.io/pypi/v/pytest-dynamodb.svg
    :target: https://pypi.python.org/pypi/pytest-dynamodb/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/wheel/pytest-dynamodb.svg
    :target: https://pypi.python.org/pypi/pytest-dynamodb/
    :alt: Wheel Status

.. image:: https://img.shields.io/pypi/pyversions/pytest-dynamodb.svg
    :target: https://pypi.python.org/pypi/pytest-dynamodb/
    :alt: Supported Python Versions

.. image:: https://img.shields.io/pypi/l/pytest-dynamodb.svg
    :target: https://pypi.python.org/pypi/pytest-dynamodb/
    :alt: License

DynamoDB fixtures for pytest.

What is this?
=============

``pytest-dynamodb`` is a pytest plugin for tests that need a running DynamoDB
instance. It provides fixtures for both a managed local process and a
connection to an already running instance.


Quickstart: first test
======================

1. Install the plugin and your test dependencies.
2. Download and unpack DynamoDB Local (see AWS docs):
   https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html
   Place extracted files in ``dynamodb_dir`` (default: ``/tmp/dynamodb``), or
   choose another location and pass it via ``--dynamodb-dir`` when running tests.
3. Make sure Java is available in your environment (DynamoDB Local runs as a JAR).
4. Write a test that uses the built-in ``dynamodb`` fixture:

.. code-block:: python

    import uuid

    def test_can_put_and_get_item(dynamodb):
        table = dynamodb.create_table(
            TableName="Test",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 10, "WriteCapacityUnits": 10},
        )

        _id = str(uuid.uuid4())
        table.put_item(Item={"id": _id, "test_key": "test_value"})
        item = table.get_item(Key={"id": _id})

        assert item["Item"]["test_key"] == "test_value"

5. Run tests:

.. code-block:: shell

    pytest

For a full example, see ``tests/test_dynamodb.py``.


How to use
==========

The plugin contains three fixtures:

* **dynamodb** - function-scoped ``DynamoDBServiceResource`` fixture.
* **dynamodb_proc** - session-scoped fixture that starts DynamoDB Local on first use and stops it at the end of the test session.
* **dynamodb_noproc** - session-scoped fixture that connects to an externally managed DynamoDB instance (for example, Docker).

When to use which fixture:

* Use ``dynamodb`` (default) when tests should manage a local process automatically.
* Use ``dynamodb_noproc`` when DynamoDB is already running elsewhere and lifecycle is managed outside pytest.

Simply include one of these fixtures in your test fixture list.

You can also create additional client and process fixtures:

.. code-block:: python

    from pytest_dynamodb import factories

    dynamodb_my_proc = factories.dynamodb_proc(port=None, delay=True)
    dynamodb_my = factories.dynamodb("dynamodb_my_proc")

.. note::

    Each DynamoDB process fixture can be configured independently using fixture factory arguments.

.. code-block:: python

    from pytest_dynamodb import factories

    dynamodb_my_noproc = factories.dynamodb_noproc(host="dynamodb", port=8088)
    dynamodb_my = factories.dynamodb("dynamodb_my_noproc")

.. note::

    ``dynamodb_noproc`` only provides connection details. Process lifecycle and data cleanup are managed by you.


Configuration
=============

You can define settings in three ways:

* ``Fixture factory argument``
* ``Command line option``
* ``Configuration option in pytest.ini``

Precedence order:

* Fixture factory argument
* Command line option
* ``pytest.ini`` option

.. list-table:: Configuration options
   :header-rows: 1

   * - DynamoDB option
     - Fixture factory argument
     - Command line option
     - pytest.ini option
     - Default
   * - Path to DynamoDB JAR directory
     - dynamodb_dir
     - --dynamodb-dir
     - dynamodb_dir
     - /tmp/dynamodb
   * - Host
     - host
     - --dynamodb-host
     - dynamodb_host
     - 127.0.0.1
   * - Port
     - port
     - --dynamodb-port
     - dynamodb_port
     - random
   * - AWS Access Key
     - access_key
     - --dynamodb-aws_access_key
     - dynamodb_aws_access_key
     - fakeMyKeyId
   * - AWS Secret Key
     - secret_key
     - --dynamodb-aws_secret_key
     - dynamodb_aws_secret_key
     - fakeSecretAccessKey
   * - AWS Region
     - region
     - --dynamodb-aws_region
     - dynamodb_aws_region
     - us-west-1
   * - `Introduce delays <https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.UsageNotes.html#:~:text=%2DdelayTransientStatuses>`_
     - delay
     - --dynamodb-delay
     - dynamodb_delay
     - false

Example usage:

* Pass as fixture factory argument:

  .. code-block:: python

      from pytest_dynamodb import factories

      dynamodb_proc = factories.dynamodb_proc(port=8888)

* Use command line option:

  .. code-block:: shell

      pytest tests --dynamodb-port=8888

* Set in ``pytest.ini``:

  .. code-block:: ini

      [pytest]
      dynamodb_port = 8888


Known issues
============

* Parallel runs with a fixed ``--dynamodb-port`` may fail because workers contend for the same port.


Package resources
=================

* Source: https://github.com/dbfixtures/pytest-dynamodb
* Bug tracker: https://github.com/dbfixtures/pytest-dynamodb/issues
