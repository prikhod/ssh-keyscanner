import argparse
import json

from redis import Redis

from search_duplicates.config import parse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="cfg file", required=True)
    args = parser.parse_args()
    cfg = parse(args.config)
    _r = Redis(host=cfg.redis.host, port=cfg.redis.port, db=cfg.redis.db, password=cfg.redis.password)

    keys = _r.hgetall('ssh_keys')

    pub_keys = [item.decode() for item in keys.values()]
    result = {}
    for host, pub_key in keys.items():
        pub_key = pub_key.decode()
        if pub_keys.count(pub_key) > 1:
            host = host.decode()
            if pub_key in result:
                result[pub_key].append(host)
            else:
                result[pub_key] = [host]

    with open('result.json', 'w') as f:
        json.dump(result, f, indent=4)
    print(json.dumps(result, indent=4))
