import asyncio
from aio_pika import connect, Message, IncomingMessage
import time
import zmq


class AlertClient:
    """Subscribe to alerts from the message broker and forward to the test orchestrator.
    """
    def __init__(self, username: str = 'testclient', password: str = 'testclient', ip: str = 'localhost', ownerid: int = 0):
        self.username = username
        self.password = password
        self.ip = ip
        self.ownerid = ownerid

        # Test orchestration connection
        context = zmq.Context()
        self.test_socket = context.socket(zmq.PUB)
        self.test_socket.bind("tcp://127.0.0.1:5002")
        time.sleep(1)

    async def run(self):
        """Publish alerts to the message broker on command from the test orchestrator.
        """
        conn = await connect(f"amqp://{self.username}:{self.password}@{self.ip}/")
        chan = await conn.channel()
        queue = await chan.declare_queue(f'lns.alerts.{self.ownerid}')

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    self.test_socket.send(message.body)  # Send to test orchestrator for verification

async def main():
    alertc = AlertClient()
    # rpcc = RpcClient()

    await asyncio.gather(
        alertc.run(),
        # rpcc.run()
    )

if __name__ == "__main__":
    asyncio.run(main())
