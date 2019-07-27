import contextlib
import ctypes
import multiprocessing as mp
import os
import signal
import socket
import sys
import threading
import unittest

import requests
import bjoern


def free_port():
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = s.getsockname()[1]
    return port


@contextlib.contextmanager
def run_bjoern(wsgi_app, host=None, port=None):
    host = host or '127.0.0.1'
    port = port or free_port()
    sock = bjoern.bind_and_listen(host, port=port)
    p = mp.Process(target=bjoern.server_run, args=(sock, wsgi_app))
    p.start()
    try:
        yield 'http://{}:{}'.format(host, port)
    finally:
        os.kill(p.pid, signal.SIGINT)
        p.join()
#        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
