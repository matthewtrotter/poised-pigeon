from typing import Optional, List
import asyncio
from aio_pika import connect, Message, IncomingMessage

class LnsBuilder:
    async def build(self, 
              ownerids: List[int] = [1,],
              username: str = 'testlns', 
              password: str = 'testlns',
              ip: str = 'localhost'
              ):
        lnss = []
        for ownerid in ownerids:
            lns = Lns(
                ownerid,
                username,
                password,
                ip
            )
            await lns.connect()
            lnss.append(lns)
        return lnss


class Lns:
    """Publish alerts to the message broker on command from the test orchestrator and respond to RPCs.
    """
    def __init__(self, 
                ownerid: int = 1, 
                username: str = 'testlns', 
                password: str = 'testlns',
                ip: str = 'localhost'
                ):
        self.username = username
        self.password = password
        self.ip = ip
        self.ownerid = ownerid
        self.alerts_queue = f'lns.alerts.{self.ownerid}'

    async def close(self):
        await self.conn.close()

    async def connect(self):
        self.conn = await connect(f"amqp://{self.username}:{self.password}@localhost/")
        self.chan = await self.conn.channel()

    async def publish_message(self, queue: str, message: bytes):
        """Publish a message to the broker

        Parameters
        ----------
        message : bytes
            bytes object to publish
        """
        await self.chan.declare_queue(queue)
        await self.chan.default_exchange.publish(
            Message(message),
            routing_key=queue,
        )
        print(f'Published: {message}')
    
    async def serve_rpc(self):
        """Listen for RPC requests, process, and respond with the procedure's result
        """
        while True:
            queue = await self.chan.declare_queue(f'lns.rpc.{self.ownerid}')
            print('Waiting for RPC request...')
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        rpc_response, queue = await self._process_rpc_request(message.body)
                        await self._publish_message(queue, rpc_response)

    async def _process_rpc_request(self, rpc_request: bytes):
        rpc_response = b'asdf'
        queue = 'asdf'
        return rpc_response, queue
