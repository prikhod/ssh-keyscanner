import asyncio
import base64
import json
from asyncio import Queue
from typing import Optional

import asyncssh
from aioredis import Redis

EXCEPTIONS = (OSError,
              ConnectionRefusedError,
              ConnectionResetError,
              asyncio.exceptions.TimeoutError,
              asyncssh.misc.ConnectionLost,
              asyncssh.misc.KeyExchangeFailed,
              )

ALGOS = ("ecdsa-sha2-nistp256",
         'ecdsa-sha2-nistp384',
         'ecdsa-sha2-nistp521',
         'ssh-ed25519',
         'ecdsa-sha2-nistp521',
         'ssh-rsa',
         'ssh-dss',
         )


class Key:
    def __init__(self, algo, pub_key):
        self.algo = algo
        self.pub_key = pub_key


async def get_key(host: str, port: int, connect_timeout: float, server_host_key_algs: list = ()) -> Optional[Key]:
    """
    Get default key from remote host or specific if server_host_key_algs has set
    :param host: host for send request
    :param port: port
    :param connect_timeout: timeout for check address
    :param server_host_key_algs: required algorithm for get key
    :return: Key structure with algorithm and public key
    """
    options = asyncssh.SSHClientConnectionOptions(connect_timeout=connect_timeout)
    try:
        key = await asyncssh.get_server_host_key(host=host,
                                                 port=port,
                                                 options=options,
                                                 server_host_key_algs=server_host_key_algs)
        return Key(key.algorithm.decode(), base64.b64encode(key.public_data).decode())
    except EXCEPTIONS:
        return None


async def process_key(host: str, port: int, _r: Redis, key: Key):
    """
    Processing getting key.
    Add to redis hset new record, update record if key change and push to stream for notification
    :param host: host
    :param port: port
    :param _r: redis client
    :param key: key
    :return:
    """
    exist = await _r.hget(name='ssh_keys', key=f'{host};{port};{key.algo}')
    if not exist:
        await _r.hset(name='ssh_keys', key=f'{host};{port};{key.algo}', value=key.pub_key)
    elif exist.decode() != key.pub_key:
        msg = {'host': host, 'port': port, 'algo': key.algo, 'old_key': exist.decode(), 'new_key': key.pub_key}
        await _r.xadd('updated_keys', {'msg': json.dumps(msg)})
        await _r.hset(name='ssh_keys', key=f'{host};{port};{key.algo}', value=key.pub_key)


async def worker(queue: Queue, _r: Redis, connect_timeout: float = 1.5) -> None:
    """
    Worker instance for scan host
    :param queue: queue with input data
    :param _r: redis client
    :param connect_timeout: timeout check each address
    :return:
    """
    while True:
        host, port = await queue.get()
        key = await get_key(host=host,
                            port=port,
                            connect_timeout=connect_timeout)
        if key:
            await process_key(host, port, _r, key)
            first_algo = key.algo
            for algo in ALGOS:
                if algo != first_algo:
                    key = await get_key(host=host,
                                        port=port,
                                        connect_timeout=connect_timeout,
                                        server_host_key_algs=[algo, ])
                    if key:
                        await process_key(host, port, _r, key)
        queue.task_done()
