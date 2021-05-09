import pytest
import asyncio
# import time
# from aio_pika import connect, Message, IncomingMessage
# import zmq

import tests.messages.lnsalerts_pb2 as la
# from google.protobuf.any_pb2 import Any

from tests.fixtures import rand_alert

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

async def test_single(factory):
    """Send and verify random alerts from one LNS to one Client
    """
    # Setup LNSs and Clients
    lnss = await factory.lns_builder().build(
        ownerids = [1,]
    )
    clients = await factory.client_builder().build(
        num=1
    )
    client_tasks = []
    for client, lns in zip(clients, lnss):
        print(lns.alerts_queue)
        await client.subscribe(lns.alerts_queue)
        client_tasks.append(asyncio.create_task(client.listen_for_alerts()))

    # Send alert
    num_alerts = 1
    seed = 1234
    for lns, client, alert in zip(lnss, clients, rand_alert(num_alerts, seed)):
        await lns.publish_message(lns.alerts_queue, alert)
        await client.wait_for_alerts(num=1, timeout=10)
        assert len(client.recvd_alerts) == num_alerts, "Client did not receive the alert."

    # Clean up
    for lns in lnss:
        await lns.close()
    for client, client_task in zip(clients, client_tasks):
        client_task.cancel()
        await client.close()
    
    assert True, "Hello world failed"



# async def test_single(lns_conns, client_conns):
#     """Send and verify random alerts from one LNS to one Client
#     """
#     for alert in rand_alert():
#         alert_bin = alert.SerializeToString()

#         # Send from LNS and receive from client
#         print(f'sending: {alert_bin}')
#         lns_conns[0].send(alert_bin)        # send alert to LNS
#         recvd_alert_bin = client_conns[0].recv()    # wait for client to receive the alert
#         print(f'received: {recvd_alert_bin}')
#         # recvd_alert = la.Alert()
#         # recvd_alert.ParseFromString(recvd_alert_bin)

#         # Verify
#         # print(alert)
#         # print()
#         # print(recvd_alert)
#         # print()
#         # print()

#     assert True, "Hello world failed"


