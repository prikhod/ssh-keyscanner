import argparse
import json
import smtplib
import ssl
import uuid

import requests
from redis import Redis, ResponseError

from notification.config import parse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="cfg file", required=True)
    args = parser.parse_args()
    cfg = parse(args.config)
    _r = Redis(host=cfg.redis.host, port=cfg.redis.port, db=cfg.redis.db, password=cfg.redis.password)
    try:
        _r.xgroup_create('updated_keys', 'notification_group', id=0, mkstream=True)
    except ResponseError as e:
        if 'BUSYGROUP Consumer Group name already exists' not in str(e):
            raise ResponseError(e)

    while True:
        #  read stream, wait for producers push data
        msg = _r.xreadgroup(
            groupname='notification_group',
            consumername=uuid.uuid4().__str__(),
            streams={'updated_keys': '>'},
            count=1,
            block=1000 * 60 * 60 * 24 * 365
        )
        info = json.loads(msg[0][1][0][1][b'msg'].decode())

        text_msg = f"""
                        Pub {info['algo']} key on host {info['host']}:{info['port']} changed \n
                        old key: {info['old_key']}
                        new key: {info['new_key']}
        """
        # send message in telegram
        data = {
            'chat_id': cfg.telegram.chat_id,
            'text': text_msg,
            'parse_mode': 'HTML'
        }
        requests.post(f'https://api.telegram.org/bot{cfg.telegram.token}/sendMessage', data=data)

        # send email
        with smtplib.SMTP_SSL(host="smtp.gmail.com", port=465, context=ssl.create_default_context()) as server:
            server.login(cfg.email.login, cfg.email.password)
            for recipient in cfg.email.recipients:
                server.sendmail(from_addr=cfg.email.login, to_addrs=recipient, msg=text_msg)
