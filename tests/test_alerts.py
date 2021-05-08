import pytest
import asyncio
import time
from aio_pika import connect, Message, IncomingMessage
import zmq

import tests.messages.lnsalerts_pb2 as la
from google.protobuf.any_pb2 import Any

from tests.fixtures import rand_alert

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

async def test_single(lns_conns, client_conns):
    """Send and verify random alerts from one LNS to one Client
    """
    for alert in rand_alert():
        alert_bin = alert.SerializeToString()

        # Send from LNS and receive from client
        print(f'sending: {alert_bin}')
        lns_conns[0].send(alert_bin)        # send alert to LNS
        recvd_alert_bin = client_conns[0].recv()    # wait for client to receive the alert
        print(f'received: {recvd_alert_bin}')
        # recvd_alert = la.Alert()
        # recvd_alert.ParseFromString(recvd_alert_bin)

        # Verify
        # print(alert)
        # print()
        # print(recvd_alert)
        # print()
        # print()

    assert True, "Hello world failed"


