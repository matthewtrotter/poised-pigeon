import asyncio
from aio_pika import connect, Message, IncomingMessage
import zmq
import zmq.asyncio
import logging
import os
import sys
import xmlrpc.server

import rpc

class MessagingServer:
    """Publish alerts to the message broker on command from the test orchestrator and respond to RPCs.
    """
    def __init__(self, username: str = 'testlns', password: str = 'testlns',
                       ip: str = 'localhost'):
        test_orchestration_port = os.getenv('TEST_ORCHESTRATION_PORT', None)
        self.username = username
        self.password = password
        self.ip = ip
        self.ownerid = test_orchestration_port
        self.alerts_queue = f'lns.alerts.{self.ownerid}'
        print(self.alerts_queue)

        # Test orchestration connection
        context = zmq.asyncio.Context()
        self.test_socket = context.socket(zmq.SUB)
        self.test_socket.connect(f'tcp://127.0.0.1:{test_orchestration_port}')
        self.test_socket.subscribe('')

    async def connect(self):
        self.conn = await connect(f"amqp://{self.username}:{self.password}@localhost/")
        self.chan = await self.conn.channel()

    async def _publish_message(self, queue: str, message: bytes):
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

    async def listen_test(self):
        """Publish alerts to the message broker on command from the test orchestrator.
        """        
        while True:
            print('Waiting for alert from test orchestrator...')
            alert_bin = await self.test_socket.recv()     # Receive from test orchestrator
            await self._publish_message(self.alerts_queue, alert_bin)
    
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
    
class RpcServer:
    async def __init__(self, username: str = 'testlns', password: str = 'testlns', ip: str = 'localhost', ownerid: int = 0):
        # Broker connection
        self.conn = await connect(f"amqp://{username}:{password}@{ip}/")
        self.chan = await self.conn.channel()
        self.queue = await self.chan.declare_queue(f'lns.rpc.{ownerid}')

    async def run(self):
        while True:
            procedure, args, response = await queue.consume(self._on_message)
            if procedure:
                result = procedure(args)
            else:
                result = None
            self._pack_response(response, result)
    
    def _on_message(self, message: IncomingMessage):
        """Parse the message and return the function to run

        Parameters
        ----------
        message : IncomingMessage
            message from the queue on the broker
        """
        # Parse into RPC Request type
        rpcrequest = lnsrpc_pb2.RpcRequest()
        rpcrequest.ParseFromString(message.body)
        
        # Determine the requested procedure to call
        request = None
        if alert.HasField('request'):
            request_bin = Any()
            request_bin.CopyFrom(rpcrequest.request)
            if request_bin.Is(lnsrpc_pb2.SwarkInfoListRequest.DESCRIPTOR):
                procedure = rpc.swark_info_list
                request = lnsrpc_pb2.SwarkInfoListRequest()
            elif request_bin.Is(lnsrpc_pb2.SwarkMuxsListRequest.DESCRIPTOR):
                procedure = rpc.swark_muxs_list
                request = lnsrpc_pb2.SwarkMuxsListRequest()
            request_bin.Unpack(request)

        return procedure, args


async def main():
    mess = MessagingServer()

    await mess.setup_broker_conn()
    await asyncio.gather(
        mess.listen_test(),
        mess.serve_rpc()
    )

if __name__ == "__main__":
    asyncio.run(main())

