import asyncio
import pytest
import time
import zmq
from tests.fixtures import SimulationFactory

@pytest.fixture
def factory():
    return SimulationFactory()
    

@pytest.fixture
async def lns_conns():
    # Create socket connections to LNSs
    lns_ports = [5001, 5002, 5003]
    sockets = [None,]*len(lns_ports)
    for i, port in enumerate(lns_ports):
        context = zmq.Context()
        sockets[i] = context.socket(zmq.PUB)
        sockets[i].bind(f'tcp://127.0.0.1:{port}')
    await asyncio.sleep(1)

    # Yield the socket to the test function
    yield sockets

    # Clean up after test is complete
    for socket in sockets:
        socket.close()


@pytest.fixture
async def client_conns():
    # Create socket connections to Clients
    client_ports = [5011, 5012, 5013]
    sockets = [None,]*len(client_ports)
    for i, port in enumerate(client_ports):
        context = zmq.Context()
        sockets[i] = context.socket(zmq.SUB)
        sockets[i].connect(f'tcp://127.0.0.1:{port}')
        sockets[i].subscribe('')
    await asyncio.sleep(1)

    # Yield the socket to the test function
    yield sockets

    # Clean up after test is complete
    for socket in sockets:
        socket.close()
