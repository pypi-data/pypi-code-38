# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest fixtures for REANA."""

from __future__ import absolute_import, print_function

import base64
import json
import os
import shutil
from uuid import uuid4

import pkg_resources
import pytest
from kombu import Connection, Exchange, Producer, Queue
from kubernetes import client
from mock import ANY, Mock, patch
from reana_commons.consumer import BaseConsumer
from reana_db.models import Base, User, Workflow
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database


@pytest.yield_fixture(scope='module')
def tmp_shared_volume_path(tmpdir_factory):
    """Fixture temporary file system database.

    Scope: module

    This fixture offers a temporary shared file system using
    ``tmpdir_factory.mktemp`` named ``reana`` and when scoped is finished
    it will be deleted.

    .. code-block:: python

        import os

        def test_dir_exists(tmp_shared_volume_path):
            path = os.path.join(
                tmp_shared_volume_path, 'directory_path')
            assert os.path.exists(path)

    """
    temp_path = str(tmpdir_factory.mktemp('reana'))
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture(scope='module')
def db_engine(base_app):
    """Create a SQL Alchemy DB engine.

    Scope: module

    This fixture offers a SQLAlchemy database engine and it expects a fixture
    called ``base_app`` which should be a configured Flask application
    including a ``SQLALCHEMY_DATABASE_URI`` configuration variable. When
    finished it will delete the database.
    """
    test_db_engine = create_engine(
        base_app.config['SQLALCHEMY_DATABASE_URI'])
    if not database_exists(test_db_engine.url):
        create_database(test_db_engine.url)
    yield test_db_engine
    drop_database(test_db_engine.url)


@pytest.fixture()
def session(db_engine):
    """Create a SQL Alchemy session.

    Scope: function

    This fixture offers a SQLAlchemy session which has been created from the
    ``db_engine`` fixture.

    .. code-block:: python

        from reana_db.models import Workflow

        def test_create_workflow(session):
            workflow = Workflow(...)
            session.add(workflow)
            session.commit()
    """
    Session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=db_engine))
    Base.query = Session.query_property()
    from reana_db.database import Session as _Session
    _Session.configure(bind=db_engine)
    yield Session
    Session.close()


@pytest.fixture()
def app(base_app, db_engine, session):
    """Flask application fixture.

    Scope: function

    This fixture offers a Flask application with already a database connection
    and all the models created. When finished it will delete all models.

    .. code-block:: python

        def create_ninja_turtle()
            with app.test_client() as client:
                somedata = 'ninja turtle'
                res = client.post(url_for('api.create_object'),
                                  content_type='application/json',
                                  data=json.dumps(somedata))

                assert res.status_code == 200

    """
    with base_app.app_context():
        import reana_db.models
        Base.metadata.create_all(bind=db_engine)
        yield base_app
        for table in reversed(Base.metadata.sorted_tables):
            db_engine.execute(table.delete())


@pytest.fixture()
def default_user(app, session):
    """Create users.

    Scope: function

    This fixture creates an user with a default UUID
    ``00000000-0000-0000-0000-000000000000``, ``email`` `info@reana.io`
    and ``access_token`` ``secretkey`` and returns it.

    .. code-block:: python

        def test_default_user_exists(default)
            with app.test_client() as client:
                res = client.post(url_for('api.get_users'),
                                  query_string={"user": default_user.id_})

                assert res.status_code == 200


    """
    default_user_id = '00000000-0000-0000-0000-000000000000'
    user = User.query.filter_by(
        id_=default_user_id).first()
    if not user:
        user = User(id_=default_user_id,
                    email='info@reana.io', access_token='secretkey')
        session.add(user)
        session.commit()
    return user


@pytest.fixture()
def serial_workflow():
    """Create a serial workflow.

    Scope: function

    This fixture provides a ``serial`` workflow.
    """
    return {
        "reana_specification": {
            "workflow": {
                "specification": {
                    "steps": [
                        {
                            "environment": "reanahub/reana-env-jupyter",
                            "commands": [
                                "echo 'Hello REANA'"
                            ]
                        }
                    ]
                },
                "type": "serial",
            },
        },
    }


@pytest.fixture()
def cwl_workflow_with_name():
    """CWL workflow with name.

    Scope: function

    This fixture provides a ``CWL`` workflow with a name as a dictionary.
    """
    return {
        "reana_specification": {
            "parameters": {"min_year": "1991", "max_year": "2001"},
            "workflow": {
                "specification": {
                    "first": "do this",
                    "second": "do that"
                },
                "type": "cwl",
            },
            "type": "cwl",
        },
        "workflow_name": "my_test_workflow",
    }


@pytest.fixture()
def yadage_workflow_with_name():
    """Yadage workflow with name.

    Scope: function

    This fixture provides a ``yadage`` workflow with a name as a dictionary.
    """
    return {
        "reana_specification": {
            "workflow": {
                "specification": {
                    "first": "do this",
                    "second": "do that"
                },
                "type": "yadage",
            },
            "parameters": {"min_year": "1991", "max_year": "2001"},
            "type": "yadage",
        },
        "name": "my_test_workflow",
    }


@pytest.fixture()
def cwl_workflow_without_name():
    """CWL workflow without name.

    Scope: function

    This fixture provides a ``CWL`` workflow without a name as a dictionary.
    """
    return {
        "reana_specification": {
            "parameters": {"min_year": "1991", "max_year": "2001"},
            "workflow": {
                "specification": {
                    "first": "do this",
                    "second": "do that"
                },
                "type": "cwl",
            },
            "type": "cwl",
        },
        "name": "",
    }


@pytest.fixture()
def yadage_workflow_without_name():
    """Yadage workflow without name.

    Scope: function

    This fixture provides a ``yadage`` workflow without name as a dictionary.
    """
    return {
        "reana_specification": {
            "workflow": {
                "specification": {
                    "first": "do this",
                    "second": "do that"
                },
                "type": "yadage",
            },
            "parameters": {"min_year": "1991", "max_year": "2001"},
            "type": "yadage",
        },
        "name": "",
    }


class _BaseConsumerTestIMPL(BaseConsumer):
    """Test implementation of a REANAConsumer class.

    This class is a basic implementation of a ``reana_commons.BaseConsumer``
    to use while testing. There are fixtures wrapping it so it shouldn't
    be used directly.
    """

    def get_consumers(self, Consumer, channel):
        """Sample get consumers method."""
        return [Consumer(self.queue, callbacks=[self.on_message],
                         accept=[self.message_default_format])]

    def on_message(self, body, message):
        """Sample on message method."""
        message.ack()


@pytest.fixture
def ConsumerBase():
    """Return a class implementing a BaseConsumer.

    Scope: function

    This fixture offers a class which implements the
    ``reana_commons.BaseConsumer``. It will just acknowledge the received
    messages.
    """
    return _BaseConsumerTestIMPL


@pytest.fixture
def ConsumerBaseOnMessageMock(ConsumerBase):
    """Return a BaseConsumer class with ``on_message`` mocked.

    Scope: function

    This fixture offers a class which implements the
    ``reana_commons.BaseConsumer``. Additionally to the ``ConsumerBase``
    fixture, this class has an ``on_message`` mocked method so actions like
    the following can be performed.

    .. code-block:: python

        def test_msg(ConsumerBaseOnMessageMock)
            consumer = ConsumerBaseOnMessageMock()
            # 1 message is published with message {'some': 'message'}
            expected_body = {'some': 'message'}
            consumer.on_message.assert_called_once_with(
                expected, ANY)

    """
    with patch.object(ConsumerBase, 'on_message'):
        yield ConsumerBase


@pytest.fixture
def consume_queue():
    """Provide a callable to consume a queue.

    Scope: function

    This fixture offers a function which given a ``kombu.Consumer`` will
    consume the messages in the queue until a certain ``limit``. If ``limit``
    is not specified it will consume uninterruptedly.

    .. code-block:: python

        def test_consume_1_msg(ConsumerBase, consume_queue)
            consumer = ConsumerBase()
            # some message is published in the queue
            # and we want to consume only one.
            consume_queue(consumer, limit=1)

    """
    def _consume_queue(consumer, limit=None):
        """Consume AMQP queue.

        :param consumer: A :class:`kombu.Consumer` to consume from.
        :param limit: Integer which represents how many items to consume
            from the queue, if not specified, the consume method will run
            uninterruptedly.
        """
        consumer_generator = consumer.consume(limit=limit)
        while True:
            try:
                next(consumer_generator)
            except StopIteration:
                # no more items to consume in the queue
                break

    return _consume_queue


@pytest.fixture(scope='session')
def in_memory_queue_connection():
    """In memory message queue.

    Scope: session

    This fixture offers an in memory :class:`kombu.Connection` scoped to the
    testing session.

    .. code-block:: python

        def test_something(ConsumerBase, in_memory_queue_connection):
            consumer = ConsumerBase(connection=in_memory_queue_connection)
            # Now you have a consumer connected to an in memory queue


    """
    return Connection('memory:///')


@pytest.fixture
def default_exchange():
    """Return a default :class:`kombu.Exchange` created from configuration.

    Scope: function

    This fixture offers a default :class:`kombu.Exchange`.
    """
    return Exchange('test-exchange', type='direct')


@pytest.fixture
def default_queue(default_exchange):
    """Return a default :class:`kombu.Queue` created from configuration.

    Scope: function

    This fixture offers a default :class:`kombu.Queue`.
    """
    return Queue('test-queue', exchange=default_exchange,
                 routing_key='test-routing-key')


@pytest.fixture
def default_in_memory_producer(in_memory_queue_connection, default_exchange):
    """Rerturn a :class:`kombu.Producer` connected to in memory queue.

    Scope: function

    This fixture offers a default :class:`kombu.Producer` instantiated using
    the ``in_memory_queue_connection``.

    .. code-block:: python

        def test_publish_hello(default_in_memory_producer, default_queue):
            msg = {'hello': 'ninja turtle'}
            default_in_memory_producer.publish(msg,
                                               declare=[default_queue])

    """
    return in_memory_queue_connection.Producer(
        exchange=default_exchange,
        routing_key='test-routing-key',
        serializer='json')


@pytest.fixture(scope='module')
def sample_workflow_workspace(tmp_shared_volume_path):
    """Return the directory path of a sample workspace.

    Scope: module

    Creates a sample workspace in the shared volume path. Copies contents from
    the ``tests/test_workspace`` directory.

    """
    def _create_sample_workflow_workspace(workflow_id):
        test_workspace_path = pkg_resources.resource_filename(
            'pytest_reana',
            'test_workspace')
        sample_workspace_path = os.path.join(tmp_shared_volume_path,
                                             str(workflow_id))
        if not os.path.exists(sample_workspace_path):
            shutil.copytree(test_workspace_path,
                            sample_workspace_path)
            yield sample_workspace_path
            shutil.rmtree(test_workspace_path,
                          sample_workspace_path)
        else:
            yield sample_workspace_path

    return _create_sample_workflow_workspace


@pytest.fixture()
def sample_yadage_workflow_in_db(app,
                                 default_user,
                                 session,
                                 yadage_workflow_with_name):
    """Create a sample workflow in the database.

    Scope: function

    Adds a sample yadage workflow in the DB.
    """
    workflow = Workflow(id_=uuid4(),
                        name='sample_serial_workflow_1',
                        owner_id=default_user.id_,
                        reana_specification=yadage_workflow_with_name[
                            'reana_specification'],
                        operational_options={},
                        type_=yadage_workflow_with_name[
                            'reana_specification']['workflow']['type'],
                        logs='')
    session.add(workflow)
    session.commit()
    yield workflow
    session.delete(workflow)
    session.commit()


@pytest.fixture()
def sample_serial_workflow_in_db(app, default_user, session, serial_workflow):
    """Create a sample workflow in the database.

    Scope: function

    Adds a sample serial workflow in the DB.
    """
    workflow = Workflow(
        id_=uuid4(),
        name='sample_serial_workflow_1',
        owner_id=default_user.id_,
        reana_specification=serial_workflow['reana_specification'],
        operational_options={},
        type_=serial_workflow['reana_specification']['workflow']['type'],
        logs='')
    session.add(workflow)
    session.commit()
    yield workflow
    session.delete(workflow)
    session.commit()


def sample_condition_for_starting_queued_workflows():
    """Sample always true condition."""
    return True


def sample_condition_for_requeueing_workflows():
    """Sample always false condition."""
    return False


@pytest.fixture
def user_secrets():
    """Test user secrets dictionary."""
    keytab_file = base64.b64encode(b'keytab file.')
    user_secrets = {
        "username": {"value": "reanauser",
                     "type": "env"},
        "password": {"value": "1232456",
                     "type": "env"},
        ".keytab": {"value": keytab_file,
                    "type": "file"}
    }
    return user_secrets


@pytest.fixture
def empty_user_secrets():
    """Empty user secrets dictionary."""
    return {}


@pytest.fixture
def corev1_api_client_with_user_secrets(default_user):
    """Kubernetes CoreV1 api client with user secrets in K8s secret store.

    Scope: function

    Adds the CoreV1APIClient with example user secrets.
    """
    def make_corev1_api_client_with_user_secrets(user_secrets):
        """Callable to return.

        Should be used with one of the secret store fixtures.
        """
        corev1_api_client = Mock()
        metadata = client.V1ObjectMeta(name=str(default_user.id_))
        metadata.annotations = {'secrets_types': '{}'}
        user_secrets_values = {}
        secrets_types = {}
        for secret_name in user_secrets:
            # Add type metadata to secret store
            secrets_types[secret_name] = \
                user_secrets[secret_name]['type']
            user_secrets_values[secret_name] = \
                user_secrets[secret_name]['value']
        metadata.annotations['secrets_types'] = json.dumps(secrets_types)
        k8s_secrets_store = client.V1Secret(
            api_version="v1",
            metadata=metadata,
            data=user_secrets_values)
        corev1_api_client.read_namespaced_secret = \
            lambda name, namespace: k8s_secrets_store
        return corev1_api_client
    return make_corev1_api_client_with_user_secrets
