"""Shared test configuration for BalatroBot tests."""

import pytest


def pytest_addoption(parser):
    """Add command line options for pytest."""
    parser.addoption(
        "--port",
        action="store",
        default=12346,
        type=int,
        help="Port number for TCP connection (default: 12346)",
    )


@pytest.fixture(scope="session")
def port(request):
    """Get the port number from command line option."""
    return request.config.getoption("--port")
