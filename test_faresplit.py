# -*- coding: utf-8 -*-
"""
    Faresplit Tests
    ~~~~~~~~~~~~

    Tests the Faresplit application.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import pytest

import os
import faresplit
import tempfile


@pytest.fixture
def client(request):
    db_fd, faresplit.app.config['DATABASE'] = tempfile.mkstemp()
    faresplit.app.config['TESTING'] = True
    client = faresplit.app.test_client()
    with faresplit.app.app_context():
        faresplit.init_db()

    def teardown():
        os.close(db_fd)
        os.unlink(faresplit.app.config['DATABASE'])
    request.addfinalizer(teardown)

    return client


def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_empty_db(client):
    """Start with a blank database."""
    rv = client.get('/')
    assert b'No entries here so far' in rv.data


def test_login_logout(client):
    """Make sure login and logout works"""
    rv = login(client, faresplit.app.config['USERNAME'],
               faresplit.app.config['PASSWORD'])
    assert b'You were logged in' in rv.data
    rv = logout(client)
    assert b'You were logged out' in rv.data
    rv = login(client, faresplit.app.config['USERNAME'] + 'x',
               faresplit.app.config['PASSWORD'])
    assert b'Invalid username' in rv.data
    rv = login(client, faresplit.app.config['USERNAME'],
               faresplit.app.config['PASSWORD'] + 'x')
    assert b'Invalid password' in rv.data


def test_messages(client):
    """Test that messages work"""
    login(client, faresplit.app.config['USERNAME'],
          faresplit.app.config['PASSWORD'])
    rv = client.post('/add', data=dict(
        title='<Hello>',
        text='<strong>HTML</strong> allowed here'
    ), follow_redirects=True)
    assert b'No entries here so far' not in rv.data
    assert b'&lt;Hello&gt;' in rv.data
    assert b'<strong>HTML</strong> allowed here' in rv.data
