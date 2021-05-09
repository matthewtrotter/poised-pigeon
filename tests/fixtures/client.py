from typing import Optional, List
import asyncio
from aio_pika import connect, Message, IncomingMessage
from collections import deque
import time

class ClientBuilder:
    async def build(self, 
              num: int = 1,
              username: str = 'testclient', 
              password: str = 'testclient',
              ip: str = 'localhost'
              ):
        clients = []
        for i in range(num):
            cl = Client(
                username,
                password,
                ip
            )
            await cl.connect()
            clients.append(cl)
        return clients


class Client:
    """Subscribe to alerts and call RPCs.
    """
    def __init__(self, 
                username: str = 'testclient', 
                password: str = 'testclient', 
                ip: str = 'localhost'
                ):
        self.username = username
        self.password = password
        self.ip = ip
        self.recvd_alerts = deque()

    async def close(self):
        await self.conn.close()

    async def connect(self):
        """Connect to message broker
        """
        self.conn = await connect(f"amqp://{self.username}:{self.password}@{self.ip}/")
        self.chan = await self.conn.channel()

    async def subscribe(self, queue: str):
        """Subscribe to a specific queue

        Parameters
        ----------
        queue : str
            Queue name on message broker
        """
        self.queue = await self.chan.declare_queue(queue)
            
    async def listen_for_alerts(self):
        """Store alerts from the message broker.
        """
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(f'Got: {message.body}')
                    self.recvd_alerts.append(message.body)

    async def wait_for_alerts(self, num: int = 1, timeout: float = 10.0):
        """Block until we get the specified number of alerts

        Parameters
        ----------
        num : int, optional
            Number of alerts to wait for in the queue, by default 1
        timeout : float, optional
            Seconds to wait for these alerts, by default 10.0
        """
        tstart = time.time()
        while time.time() < tstart + timeout:
            if len(self.recvd_alerts) >= num:
                break
            await asyncio.sleep(0.1)
