#!/usr/bin/env bash
set -e

# install libev
# Note: brew update is extremely slow on travis
# brew install libev
curl http://dist.schmorp.de/libev/libev-${LIBEV_VERSION}.tar.gz --silent --output /tmp/libev-${LIBEV_VERSION}.tar.gz
tar xf /tmp/libev-${LIBEV_VERSION}.tar.gz -C /tmp/
pushd /tmp/libev-${LIBEV_VERSION}
./configure
popd
make -C /tmp/libev-${LIBEV_VERSION}/
make install -C /tmp/libev-${LIBEV_VERSION}/

# install python
INSTALLER_URL=https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-macosx10.9.pkg
INSTALLER=${INSTALLER_URL##*/}
curl $INSTALLER_URL --silent --output /tmp/$INSTALLER
sudo installer -pkg /tmp/$INSTALLER -target /
export PATH=$PATH:/Library/Frameworks/Python.framework/Versions/${TRAVIS_PYTHON_VERSION}/bin:$HOME/Library/Python/${TRAVIS_PYTHON_VERSION}/bin

# install tox and run the pipeline
python${TRAVIS_PYTHON_VERSION} -m pip install tox
tox -vv

# build sdist if the job defines SDIST env var
if [ -n "$SDIST" ]; then
  python${TRAVIS_PYTHON_VERSION} setup.py sdist
  cp dist/bjoern-*.tar.gz wheelhouse
fi

# don't use travis-dpl and pypi provider for releasing to PyPI as not working on MacOS
if [ -n "$TRAVIS_TAG" ]; then
  python${TRAVIS_PYTHON_VERSION} -m pip install twine
  twine upload wheelhouse/*
fi
