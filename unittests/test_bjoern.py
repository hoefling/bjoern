import json
import os
import unittest
import requests

from urllib.parse import urljoin

from .utils import run_bjoern


# rm -rf _bjoern.cpython-36m-x86_64-linux-gnu.so build/ __pycache__/ && CFLAGS="-coverage" CC="gcc" LDFLAGS="-coverage -lgcov" LDSHARED="gcc -pthread -shared" pip install -vvv --editable .

class BjoernTests(unittest.TestCase):

    def test_status_codes(self):
        data = (
            ('200 ok', 200), ('201 created', 201),
            ('202 accepted', 202), ('204 no content', 204),
        )
        for text, code in data:
            with self.subTest(response=text, status_code=code):
                def app(e, s):
                    s(response, [])
                return b''
            with run_bjoern(app) as url:
                resp = requests.get(url)
                self.assertEqual(resp.status_code, status_code)

    def test_empty_content(self):
        def app(e, s):
            s('200 ok', [])
            return b''
        with run_bjoern(app) as url:
            response = requests.get(url)
            self.assertEqual(response.content, b'')

    def test_env(self):
        def app(env, start_response):
            start_response('200 yo', [])
            key = 'REQUEST_METHOD'
            return ['{}: {}'.format(key, env[key]).encode()]

        with run_bjoern(app) as url:
            response = requests.get(url)
            self.assertEqual(response.text, 'REQUEST_METHOD: GET')

    def test_invalid_header_type(self):
        def app(environ, start_response):
            start_response('200 ok', None)
            return ['yo']

        with run_bjoern(app) as url:
            response = requests.get(url)
            self.assertEqual(response.status_code, 500)

    def test_invalid_header_tuple(self):
        tuples = [(), ('a', 'b', 'c'), ('a',)]
        for headers in tuples:
            with self.subTest(headers=headers):
                def app(environ, start_response):
                    start_response('200 ok', headers)
                    return ['yo']

                with run_bjoern(app) as url:
                    response = requests.get(url)
                    self.assertEqual(response.status_code, 500)

    def test_invalid_header_tuple_item(self):
        def app(environ, start_response):
            start_response('200 ok', (object(), object()))
            return ['yo']

        with run_bjoern(app) as url:
            response = requests.get(url)
            self.assertEqual(response.status_code, 500)

    def test_send_file(self):
        files = {
            'small' : 888,
            'big' : 88888
        }
        for name, size in files.items():
            new_name = '/tmp/bjoern.%s.tmp' % name
            with open(new_name, 'wb') as f:
                f.write(os.urandom(size))
            files[name] = new_name

        def app(env, start_response):
            start_response('200 ok', [])
            if env['PATH_INFO'].startswith('/big'):
                return open(files['big'], 'rb')
            return open(files['small'], 'rb')

        data = [('/big', files['big']), ('/small', files['small'])]
        for path, filename in data:
            with self.subTest(path=path, filename=filename):
                with run_bjoern(app) as url:
                    response = requests.get(urljoin(url, path))
                with open(filename, 'rb') as f:
                    expected = f.read()
                self.assertEqual(response.content, expected)
