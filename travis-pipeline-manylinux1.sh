#!/usr/bin/env bash

# This script expects to be executed inside a manylinux container. Example usage:
# docker run --rm --tty -e TOXENV -e TRAVIS_TAG -e TWINE_USERNAME -e TWINE_PASSWORD -e TWINE_REPOSITORY -e LIBEV_VERSION \
# -v $(pwd):/io quay.io/pypa/manylinux_x86_64:latest bash -c /io/travis-pipeline-manylinux1.sh
set -e

# install libev
curl http://dist.schmorp.de/libev/libev-${LIBEV_VERSION}.tar.gz --silent --output /tmp/libev-${LIBEV_VERSION}.tar.gz
tar xf /tmp/libev-${LIBEV_VERSION}.tar.gz -C /tmp/
pushd /tmp/libev-${LIBEV_VERSION}
./configure
popd
make -C /tmp/libev-${LIBEV_VERSION}/
make install -C /tmp/libev-${LIBEV_VERSION}/

# install tox
export PATH=/opt/python/cp37-cp37m/bin:$PATH
pip install tox
tox -vv -c /io/tox.ini

if [ -n "$TRAVIS_TAG" ]; then
  pip install twine
  twine upload /io/wheelhouse/*
fi
