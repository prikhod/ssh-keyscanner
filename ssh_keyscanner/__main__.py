import argparse
import asyncio
import ipaddress
from typing import List, Tuple

import aioredis

from ssh_keyscanner.config import parse, RedisCfg
from ssh_keyscanner.worker import worker


async def process(hosts: List[Tuple[str, int]], cfg_redis: RedisCfg, num_workers: int, connect_timeout: float) -> None:
    """
    Create queue, workers, run tasks
    :param hosts: list of tuple with host and port for scan
    :param cfg_redis: redis config data
    :param num_workers: number of workers witch async scan addresses
    :param connect_timeout: timeout for every ssh connection
    :return:
    """
    _r = await aioredis.Redis(host=cfg_redis.host, port=cfg_redis.port, db=cfg_redis.db, password=cfg_redis.password)
    queue = asyncio.Queue()
    for address in hosts:
        queue.put_nowait(address)
    tasks = []
    for i in range(num_workers):
        task = asyncio.create_task(worker(queue, _r, connect_timeout=connect_timeout))
        tasks.append(task)
    await queue.join()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="cfg file", required=True)
    subparsers = parser.add_subparsers()

    group_source = parser.add_mutually_exclusive_group(required=True)
    group_source.add_argument("-f", "--file", help="hosts file, line format: 'host:port'")
    group_source.add_argument("-a", "--host", help="host or network: 192.0.2.0 or 192.0.2.0/27")
    parser.add_argument("-p", "--port", help="port")

    args = parser.parse_args()
    cfg = parse(args.config)

    if args.file:
        with open(args.file, 'r') as f:
            def parse_line(address):
                return address.strip().split(':')[0], int(address.strip().split(':')[1])
            _hosts = [parse_line(address) for address in f]
    else:
        net = ipaddress.IPv4Network(args.host)
        port = int(args.port) if args.port else 22
        _hosts = [(str(host), port) for host in net.hosts()]

    asyncio.run(process(_hosts, cfg_redis=cfg.redis, num_workers=cfg.num_workers, connect_timeout=cfg.connect_timeout))
