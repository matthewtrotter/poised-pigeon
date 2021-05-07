import asyncio
from aio_pika import connect, Message, IncomingMessage
import zmq
import logging

import rpc

class AlertServer:
    """Publish alerts to the message broker on command from the test orchestrator.
    """
    def __init__(self, username: str = 'testlns', password: str = 'testlns',
                       ip: str = 'localhost', ownerid: int = 0):
        self.username = username
        self.password = password
        self.ip = ip
        self.ownerid = ownerid

        # Test orchestration connection
        print('starting zmq')
        context = zmq.Context()
        self.test_socket = context.socket(zmq.SUB)
        self.test_socket.connect(f'tcp://127.0.0.1:5001')
        self.test_socket.subscribe('')
        print('subscribed zmq')

    async def _setup_broker_conn(self):
        print('starting broker connection')

        self.conn = await connect(f"amqp://{self.username}:{self.password}@localhost/")
        self.chan = await self.conn.channel()
        self.queue = f'lns.alerts.{self.ownerid}'
        await self.chan.declare_queue(self.queue)
        print('got broker connection')

    async def run(self):
        """Publish alerts to the message broker on command from the test orchestrator.
        """
        await self._setup_broker_conn()
        
        while True:
            print('Waiting for alert from test orchestrator...')
            alert_bin = self.test_socket.recv()     # Receive from test orchestrator
            print(alert_bin)
            print(type(alert_bin))
            await self.chan.default_exchange.publish(
                Message(alert_bin),
                routing_key=self.queue,
            )
    
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
    alerts = AlertServer()
    # rpcs = RpcServer()
    print('hi')

    await asyncio.gather(
        alerts.run(),
        # rpcs.run()
    )

if __name__ == "__main__":
    print('hi')
    asyncio.run(main())
