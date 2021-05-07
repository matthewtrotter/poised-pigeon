import asyncio
import pytest
import time
import zmq

@pytest.fixture
async def lns_conn(port: int = 5001):
    # Create socket connection to LNS
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f'tcp://127.0.0.1:{port}')
    await asyncio.sleep(1)

    # Yield the socket to the test function
    yield socket

    # Clean up after test is complete
    socket.close()


@pytest.fixture
async def client_conn(port: int = 5002):
    # Create socket connection to Client
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f'tcp://127.0.0.1:{port}')
    socket.subscribe('')
    await asyncio.sleep(1)

    # Yield the socket to the test function
    yield socket

    # Clean up after test is complete
    socket.close()
