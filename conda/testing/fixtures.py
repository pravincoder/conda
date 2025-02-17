# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
import warnings

import py
import pytest

from conda.auxlib.ish import dals
from conda.base.context import context, reset_context
from conda.common.configuration import YamlRawParameter
from conda.common.serialize import yaml_round_trip_load
from conda.core.subdir_data import SubdirData
from conda.gateways.disk.create import TemporaryDirectory


@pytest.fixture(autouse=True)
def suppress_resource_warning():
    """
    Suppress `Unclosed Socket Warning`

    It seems urllib3 keeps a socket open to avoid costly recreation costs.

    xref: https://github.com/kennethreitz/requests/issues/1882
    """
    warnings.filterwarnings("ignore", category=ResourceWarning)


@pytest.fixture(scope="function")
def tmpdir(tmpdir, request):
    tmpdir = TemporaryDirectory(dir=str(tmpdir))
    request.addfinalizer(tmpdir.cleanup)
    return py.path.local(tmpdir.name)


@pytest.fixture(autouse=True)
def clear_subdir_cache():
    SubdirData.clear_cached_local_channel_data()


@pytest.fixture(scope="function")
def disable_channel_notices():
    """
    Fixture that will set "context.number_channel_notices" to 0 and then set
    it back to its original value.

    This is also a good example of how to override values in the context object.
    """
    yaml_str = dals(
        """
        number_channel_notices: 0
        """
    )
    reset_context(())
    rd = {
        "testdata": YamlRawParameter.make_raw_parameters(
            "testdata", yaml_round_trip_load(yaml_str)
        )
    }
    context._set_raw_data(rd)

    yield

    reset_context(())


@pytest.fixture(scope="function")
def reset_conda_context():
    """
    Resets the context object after each test function is run.
    """
    yield

    reset_context()
