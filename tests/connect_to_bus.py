# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2020, Battelle Memorial Institute.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government. Neither the United States Government nor the
# United States Department of Energy, nor Battelle, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufactufrer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by
# BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# }}}
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import parse_qs, urlsplit, urlunsplit

import zmq.green as zmq

from volttron.client.known_identities import CONTROL_CONNECTION
from volttron.messagebus.zmq.green import Socket as GreenSocket
from volttron.types.bases import Connection, Message

zmq.context.instance()

# TODO ADD BACK rmq
# from volttron.client.vip.rmq_connection import BaseConnection
_log = logging.getLogger(__name__)


@dataclass
class ZmqConnectionContext:
    address: str = None
    identity: str = None
    publickey: str = None
    secretkey: str = None
    serverkey: str = None
    agent_uuid: str = None
    reconnect_interval: int = None


if __name__ == '__main__':
    import json
    keys = json.loads(Path(f"~/.volttron/credentials_store/{CONTROL_CONNECTION}.json").expanduser().open().read())
    server_keys = json.loads(
        Path(f"~/.volttron/credentials_store/{CONTROL_CONNECTION}.json").expanduser().open().read())

    conn_context = ZmqConnectionContext(address="tcp://127.0.0.1:22916",
                                        identity=keys["identity"],
                                        publickey=keys["publickey"],
                                        secretkey=keys["secretkey"],
                                        serverkey=server_keys["publickey"])

    from volttron.zmq.utils import encode_key

    def _add_keys_to_addr(address: str) -> str:
        '''Adds public, secret, and server keys to query in VIP address if
        they are not already present'''

        def add_param(query_str, key, value):
            query_dict = parse_qs(query_str)
            if not value or key in query_dict:
                return ''
            # urlparse automatically adds '?', but we need to add the '&'s
            return '{}{}={}'.format('&' if query_str else '', key, value)

        url = list(urlsplit(address))

        if url[0] in ['tcp', 'ipc']:
            url[3] += add_param(url[3], 'publickey', encode_key(conn_context.publickey))
            url[3] += add_param(url[3], 'secretkey', encode_key(conn_context.secretkey))
            url[3] += add_param(url[3], 'serverkey', encode_key(conn_context.serverkey))

        return str(urlunsplit(url))

    address_with_keys = _add_keys_to_addr(conn_context.address)
    zmq_context = zmq.Context()

    socket = GreenSocket(zmq.DEALER)

    socket.connect(address_with_keys)
