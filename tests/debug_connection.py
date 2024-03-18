# import volttrontesting as vt

# def test_can_find_zmqcore():
#     from volttron.server.server_options import _ServerOptions, _ServerRuntime

#     vhome = vt.create_volttron_home()
#     options = _ServerOptions(volttron_home=vhome, message_bus="zmq")
#     assert "zmq" == options.message_bus
#     runtime = _ServerRuntime(options)

import logging
import os
import random

import coloredlogs
import gevent
import zmq.green as zmq

zmq_context = zmq.Context.instance()
logging.basicConfig(level=logging.DEBUG)
coloredlogs.install(level=logging.DEBUG)
from pathlib import Path

from volttron.client.vip.agent import Agent
from volttron.types import Message
from volttron.types.auth import PKICredentials
from volttron.types.blinker import volttron_home_set_evnt
from volttron.types.known_host import \
    KnownHostProperties as known_host_properties
from volttron.utils import jsonapi

from volttron.messagebus.zmq.socket import Address
from volttron.messagebus.zmq.zmq_connection import (ZmqConnection, ZmqConnectionContext)
from volttron.messagebus.zmq.zmq_core import (ZmqConnectionBuilder, ZmqCore, ZmqCoreBuilder)

os.environ['VOLTTRON_HOME'] = Path("~/.volttron").expanduser().as_posix()
volttron_home_set_evnt.send(None)

_log = logging.getLogger(__name__)
path = Path("~/.volttron").expanduser()
creds_path = path / "credentials_store/control.connection.json"
server_creds_path = path / "credentials_store/server.json"
server_creds = jsonapi.loads(server_creds_path.open().read())
creds = jsonapi.loads(creds_path.open().read())
ipc = f'ipc://@{path.as_posix()}/run/vip.socket'
tcp = f'tcp://127.0.0.1:22916'

addr = ipc

_log.debug(f"SEnding Address: {addr}")
context = ZmqConnectionContext(identity="control.connection",
                               address=addr,
                               publickey=creds['publickey'],
                               secretkey=creds['secretkey'],
                               serverkey=server_creds['publickey'])

control_creds = PKICredentials(identity="control.connection",
                               publickey=creds['publickey'],
                               secretkey=creds['secretkey'])

agent = Agent(address=addr, identity="control.connection", credentials=control_creds)
#core = ZmqCore(None, address=tcp, credentials=foo_creds)

event = gevent.event.Event()

gevent.spawn(agent.core.run, event)

event.wait()

print(f"Is connected? {agent.core.connected}")
agent.core.stop()

#conn = ZmqConnection(conn_context=context, zmq_context=zmq_context)
#ident = 'foo.' + str(random.random())

    #message = Message(peer="", subsystem="hello", msg_id=ident, args=["hello"])

    # def on_connect_callback(success: bool):
    #     print("I am connected")

    # conn.connect(on_connect_callback)
    # conn.send_vip_message(message=message)

    # resp = conn.recieve_vip_message()
    # print(resp)
