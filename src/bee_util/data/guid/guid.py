# Ported from https://github.com/graham/python_xid which almost a direct copy of xid(https://github.com/rs/xid)


from bee_util.data.guid import base32hex

import hashlib
import platform
import os
import time
import datetime
import threading

from bee_util.errors.error import BeeError


class InvalidGuidError(BeeError):
    pass

trimLen = 20
encodedLen = 24
decodedLen = 14
rawLen = 12


def read_int():
    # type: () -> int
    buf = str(os.urandom(3))
    buford = list(map(ord, buf))
    return buford[0] << 16 | buford[1] << 8 | buford[2]


def read_machine_id():
    """
    read machine's id
    """
    try:
        hostname = platform.node()
        hw = hashlib.md5()
        hw.update(hostname.encode('utf-8'))
        # return md5.hexdigest()
        val = str(hw.digest()[:3])
        return list(map(ord, val))
    except:
        buf = os.urandom(3)
        return list(map(ord, str(buf)))


pid = os.getpid()
machineID = read_machine_id()
lock = threading.Lock()


def generateNextId():
    id = read_int()

    while True:
        new_id = id + 1
        id += 1
        yield new_id


objectIDGenerator = generateNextId()


def generate_new_xid():
    # type: () -> List[int]
    now = int(time.time())
    id = [0] * rawLen

    id[0] = (now >> 24) & 0xff
    id[1] = (now >> 16) & 0xff
    id[2] = (now >> 8) & 0xff
    id[3] = (now) & 0xff

    id[4] = machineID[0]
    id[5] = machineID[1]
    id[6] = machineID[2]

    id[7] = (pid >> 8) & 0xff
    id[8] = (pid) & 0xff

    lock.acquire()
    i = next(objectIDGenerator)
    lock.release()

    id[9] = (i >> 16) & 0xff
    id[10] = (i >> 8) & 0xff
    id[11] = (i) & 0xff

    return id


class Guid(object):
    def __init__(self, id=None):
        # type: (List[int]) -> None
        if id is None:
            id = generate_new_xid()
        self.value = id

    def pid(self):
        # type: () -> int
        return (self.value[7] << 8 | self.value[8])

    def counter(self):
        # type: () -> int
        return (self.value[9] << 16 |
                self.value[10] << 8 |
                self.value[11])

    def machine(self):
        # type: () -> str
        return ''.join(map(chr, self.value[4:7]))

    def datetime(self):
        return datetime.datetime.fromtimestamp(self.time())

    def time(self):
        # type: () -> int
        return (self.value[0] << 24 |
                self.value[1] << 16 |
                self.value[2] << 8 |
                self.value[3])

    def string(self):
        # type: () -> str
        byte_value = self.bytes()
        return base32hex.b32encode(byte_value).lower()[:trimLen]

    def bytes(self):
        # type: () -> str
        return ''.join(map(chr, self.value))

    def __repr__(self):
        return "<Guid '%s'>" % self.__str__()

    def __str__(self):
        return self.string()

    def __lt__(self, arg):
        # type: (Guid) -> bool
        return self.string() < arg.string()

    def __gt__(self, arg):
        # type: (Guid) -> bool
        return self.string() > arg.string()

    @classmethod
    def from_string(cls, s):
        # type: (str) -> Guid
        val = base32hex.b32decode(s.upper())
        value_check = [0 <= x < 255 for x in val]

        if not all(value_check):
            raise InvalidGuidError(s)

        return cls(val)


