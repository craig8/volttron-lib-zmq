from __future__ import annotations

import logging
import struct
from json import JSONDecodeError
from typing import Any

from volttron.utils import jsonapi, logtrace

# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
#                 Installable Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2022 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# ===----------------------------------------------------------------------===
# }}}

_log = logging.getLogger(__name__)

ENCODE_FORMAT = "ISO-8859-1"


def deserialize_frames(frames: List[Frame]) -> List:
    decoded = []

    for x in frames:
        if isinstance(x, list):
            decoded.append(deserialize_frames(x))
        elif isinstance(x, int):
            decoded.append(x)
        elif isinstance(x, float):
            decoded.append(x)
        elif isinstance(x, bytes):
            decoded.append(x.decode(ENCODE_FORMAT))
        elif isinstance(x, str):
            decoded.append(x)
        elif x is not None:
            # _log.debug(f'x is {x}')
            if x == {}:
                decoded.append(x)
                continue
            try:
                d = x.bytes.decode(ENCODE_FORMAT)
            except UnicodeDecodeError as e:
                _log.error(f"Unicode decode error: {e}")
                decoded.append(x)
                continue
            try:
                decoded.append(jsonapi.loads(d))
            except JSONDecodeError:
                decoded.append(d)
    return decoded


# def deserialize_frames(frames: list[bytes]) -> list:
#     decoded = []

#     for x in frames:
#         if x is not None:
#             if x == {}:
#                 decoded.append(x)
#                 continue
#         try:
#             if isinstance(x, int):
#                 value = x
#             elif isinstance(x, bytes):
#                 value = x.decode(ENCODE_FORMAT)
#             else:
#                 value = x.bytes.decode(ENCODE_FORMAT)
#         except AttributeError:
#             value = deserialize_frames(x)

#         #_log.debug(f"Deserialization:\ntype: {type(x)!r} ({x!r})\nto {type(value)!r} ({value!r})")
#         # value = str(x)
#         # print(f"frame value is {x}")
#         # if value.startswith("[") and value.endswith("]"):
#         #     value = deserialize_frames(x)

#         decoded.append(value)

#         # if isinstance(x, list):
#         #     decoded.append(deserialize_frames(x))
#         # elif isinstance(x, int):
#         #     decoded.append(x)
#         # elif isinstance(x, float):
#         #     decoded.append(x)
#         # elif isinstance(x, bytes):
#         #     decoded.append(x.decode(ENCODE_FORMAT))
#         # elif isinstance(x, str):
#         #     decoded.append(x)
#         # elif x is not None:
#         #     if x == {}:
#         #         decoded.append(x)
#         #         continue
#         #     try:
#         #         d = x.decode(ENCODE_FORMAT)
#         #     except UnicodeDecodeError as e:
#         #         _log.error(f"Unicode decode error: {e}")
#         #         decoded.append(x)
#         #         continue
#         # try:
#         #     decoded.append(jsonapi.loads(d))
#         # except JSONDecodeError:
#         #     decoded.append(d)
#     return decoded


def serialize_frames(data: list[Any]) -> list[bytes]:
    frames = []

    for x in data:
        try:
            if isinstance(x, list) or isinstance(x, dict):
                frames.append(jsonapi.dumps(x).encode(ENCODE_FORMAT))
            elif isinstance(x, bytes):
                frames.append(x)
            elif isinstance(x, bool):
                frames.append(struct.pack("?", x))
            elif isinstance(x, int):
                frames.append(struct.pack("I", x))
            elif isinstance(x, float):
                frames.append(struct.pack("f", x))
            elif x is None:
                frames.append(None)
            else:
                frames.append(x.encode(ENCODE_FORMAT))
        except TypeError as e:
            import sys
            sys.exit(0)
        except AttributeError as e:
            import sys
            sys.exit(0)
    return frames
