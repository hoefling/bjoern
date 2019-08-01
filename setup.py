import os
import glob
from setuptools import setup, Extension


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as fp:
    README = fp.read()

SOURCE_FILES = [os.path.join('http-parser', 'http_parser.c')] + \
               sorted(glob.glob(os.path.join('bjoern', '*.c')))

bjoern_extension = Extension(
    '_bjoern',
    sources       = SOURCE_FILES,
    libraries     = ['ev'],
    include_dirs  = ['http-parser', '/usr/include/libev', '/opt/local/include'],
    define_macros = [('WANT_SENDFILE', '1'),
                     ('WANT_SIGINT_HANDLING', '1'),
                     ('WANT_SIGNAL_HANDLING', '1'),
                     ('SIGNAL_CHECK_INTERVAL', '0.1')],
    extra_compile_args = ['-std=c99', '-fno-strict-aliasing', '-fcommon',
                          '-fPIC', '-Wall', '-Wextra', '-Wno-unused-parameter',
                          '-Wno-missing-field-initializers', '-g']
)

setup(
    name             = 'bjoern',
    author           = 'Jonas Haag',
    author_email     = 'jonas@lophus.org',
    license          = '2-clause BSD',
    url              = 'https://github.com/jonashaag/bjoern',
    description      = 'A screamingly fast Python 2 + 3 WSGI server written in C.',
    long_description = README,
    version          = '3.0.1',
    classifiers      = ['Development Status :: 4 - Beta',
                        'License :: OSI Approved :: BSD License',
                        'Programming Language :: C',
                        'Programming Language :: Python :: 2',
                        'Programming Language :: Python :: 3',
                        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server'],
    py_modules       = ['bjoern'],
    ext_modules      = [bjoern_extension]
)
