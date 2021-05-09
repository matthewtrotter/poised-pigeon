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
        self.test_socket = context.socket(zmq.REP)
        self.test_socket.bind("tcp://127.0.0.1:5002")
        time.sleep(1)

    async def listen_test(self):
        """Respond to the test orchestrator.
        """        
        while True:
            print('Waiting for command from test orchestrator...')
            message = await self.test_socket.recv()     # Receive from test orchestrator
            request, details = message.split(" ||| ")
            if request == 'last message?':
                self.test_socket.send(self.last_alert)
            elif request == 'subscribe':
                self.queue = await chan.declare_queue(str(details))
            elif request == 'send rpc':
                rpc_response = await self._send_rpc_request(self.rpc_queue, details)
                self.test_socket.send(rpc_response)     # Send the RPC response to the test orchestrator 
            
    async def subscribe_to_alerts(self):
        """Subscribe to the message broker.
        """
        conn = await connect(f"amqp://{self.username}:{self.password}@{self.ip}/")
        chan = await conn.channel()

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    self.test_socket.send(message.body)  # Send to test orchestrator for verification

async def main():
    alertc = AlertClient()

    await asyncio.gather(
        alertc.run()
    )

if __name__ == "__main__":
    asyncio.run(main())
