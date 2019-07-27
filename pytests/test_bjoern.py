import json
import os
import unittest
import requests
import sys

import pytest
import bjoern

from .utils import run_bjoern


# rm -rf _bjoern.cpython-36m-x86_64-linux-gnu.so build/ __pycache__/ && CFLAGS="-coverage" CC="gcc" LDFLAGS="-coverage -lgcov" LDSHARED="gcc -pthread -shared" pip install -vvv --editable .


@pytest.mark.parametrize('content,status_code', (
    ('200 ok', 200), ('201 created', 201),
    ('202 accepted', 202), ('204 no content', 204),
))
def test_status_codes(content, status_code):
    """tests/204.py"""
    def app(e, s):
        s(content, [])
        return b''
    with run_bjoern(app) as url:
        resp = requests.get(url)
        assert resp.status_code == status_code


def test_empty_content():
    """tests/empty.py"""
    def app(e, s):
        s('200 ok', [])
        return b''
    with run_bjoern(app) as url:
        response = requests.get(url)
        assert response.content == b''


def test_env():
    """tests/env.py"""
    def app(env, start_response):
        start_response('200 yo', [])
        key = 'REQUEST_METHOD'
        return ['{}: {}'.format(key, env[key]).encode()]

    with run_bjoern(app) as url:
        response = requests.get(url)
        assert response.text == 'REQUEST_METHOD: GET'


def test_invalid_header_type():
    """tests/all-kinds-of-errors.py"""
    def app(environ, start_response):
        start_response('200 ok', None)
        return ['yo']

    with run_bjoern(app) as url:
        response = requests.get(url)
        assert response.status_code == 500


@pytest.mark.parametrize('headers', (
    (), ('a', 'b', 'c'), ('a',)
), ids=str)
def test_invalid_header_tuple(headers):
    """tests/all-kinds-of-errors.py"""
    def app(environ, start_response):
        start_response('200 ok', headers)
        return ['yo']

    with run_bjoern(app) as url:
        response = requests.get(url)
        assert response.status_code == 500


def test_invalid_header_tuple_item():
    """tests/all-kinds-of-errors.py"""
    def app(environ, start_response):
        start_response('200 ok', (object(), object()))
        return ['yo']

    with run_bjoern(app) as url:
        response = requests.get(url)
        assert response.status_code == 500


@pytest.fixture(params=[('small.tmp', 888), ('big.tmp', 88888)], ids=lambda s: s[0])
def temp_file(request, tmp_path):
    name, size = request.param
    file = tmp_path / name
    with file.open('wb') as f:
        f.write(os.urandom(size))
    return file


@pytest.mark.skip
def test_send_file(temp_file):
    """tests/file.py"""
    def app(env, start_response):
        start_response('200 ok', [])
        return temp_file.open('rb')

    with run_bjoern(app) as url:
        response = requests.get(url)
    assert response.content == temp_file.read_bytes()


def test_wsgi_app_not_callable():
    """tests/not-callable.py"""
    with run_bjoern(object()) as url:
        response = requests.get(url)
    assert response.status_code == 500


def test_iter_response():
    """tests/huge.py"""
    N = 1024
    CHUNK = b'a' * 1024
    DATA_LEN = N * len(CHUNK)

    class _iter(object):
        def __iter__(self):
            for i in range(N):
                yield CHUNK

    def app(e, s):
        s('200 ok', [('Content-Length', str(DATA_LEN))])
        return _iter()

    with run_bjoern(app) as url:
        response = requests.get(url)
    assert response.content == b'a' * 1024 * 1024


def test_tuple_response():
    """tests/slow_server.py"""
    def app(environ, start_response):
        start_response('200 OK', [('Content-Type','text/plain')])
        return (b'Hello,', b" it's me, ", b'Bob!')

    with run_bjoern(app) as url:
        response = requests.get(url)
    assert response.content == b"Hello, it's me, Bob!"


#@pytest.mark.xfail(sys.version_info >= (3, 6), reason='fails with python3.6/3.7')
def test_huge_response():
    """tests/slow_server.py"""
    def app(environ, start_response):
        start_response('200 OK', [('Content-Type','text/plain')])
        return [b'x'*(1024*1024)]

    with run_bjoern(app) as url:
        response = requests.get(url)
    assert response.content == b'x' * 1024 * 1024
