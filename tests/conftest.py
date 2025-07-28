"""Shared test configuration for BalatroBot tests."""

import pytest


def pytest_addoption(parser):
    """Add command line options for pytest."""
    parser.addoption(
        "--port",
        action="append",
        type=int,
        help="Port number for Balatro instance (use multiple times for parallel execution)",
    )


def pytest_configure(config):
    """Configure ports and distribution."""
    ports = config.getoption("--port") or [12346]

    # Remove duplicates while preserving order
    unique_ports = []
    for port in ports:
        if port not in unique_ports:
            unique_ports.append(port)

    config._balatro_ports = unique_ports

    if len(unique_ports) > 1:
        config.option.dist = "loadscope"


@pytest.fixture(scope="session")
def port(request, worker_id):
    """Get assigned port for this worker."""
    ports = getattr(request.config, "_balatro_ports", [12346])

    if worker_id == "master":
        return ports[0]

    worker_num = int(worker_id.replace("gw", ""))
    return ports[worker_num % len(ports)]
