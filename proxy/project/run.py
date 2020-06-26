import os
import sys
import logging
import struct
import time
import calendar
import asyncio
import redis
import jwt

from aiohttp import web, ClientSession
from redis.exceptions import ConnectionError
from urllib.parse import urljoin
from datetime import datetime

REDIS_URL = os.getenv('REDIS_URL', 'redis')
print(REDIS_URL)
PROXY_TARGET = os.getenv('PROXY_TARGET', 'https://reqres.in')
print(PROXY_TARGET)
JWT_SECRET = os.getenv(
    'JWT_SECRET',
    'a9ddbcaba8c0ac1a0a812dc0c2f08514b23f2db0a68343cb8199ebb38a6d91e4ebfb378e22ad39c2d01 d0b4ec9c34aa91056862ddace3fbbd6852ee60c36acbf'
)
JWT_ALG = os.getenv('JWT_ALG', 'HS512')
JWT_HEADER = os.getenv('JWT_HEADER', 'x-my-jwt')

HTTP_PORT = 9000

logger = logging.getLogger("proxy")
start_time = time.time()


def get_jwt():
    sjwt = get_bjwt()
    return sjwt.decode()


def get_bjwt():
    timestamp = calendar.timegm(datetime.today().timetuple())
    this = jwt.encode(
        payload={"user": "username", "date": timestamp},
        key=JWT_SECRET,
        algorithm=JWT_ALG,
    )
    logger.info(f'JWT generated on date {datetime.today()} with user username and timespamp {timestamp}')
    return this


def inc_requests_count():
    r = redis.StrictRedis(REDIS_URL)
    try:
        if r.get('counter') == None:
            r.set('counter', 0)
        r.incr("counter")
    except ConnectionError:
        logger.info('Connetion error to Redis')
        pass


def get_requests_count():
    r = redis.StrictRedis(REDIS_URL)
    try:
        count = r.get('counter').decode('UTF-8')
    except ConnectionError:
        count = 0
    return count


def get_uptime():
    global start_time
    return time.time() - start_time


def render_status():
    return f'Processed {get_requests_count()} requests. Uptime {get_uptime()} sec'


async def handler(request):
    logger.info(f'handled {request.rel_url}')

    if str(request.rel_url).lower().strip('/') == 'status':
        return web.Response(text=render_status(), status=200)

    async with ClientSession() as session:
        async with session.get(urljoin(PROXY_TARGET, str(request.rel_url))) as resp:
            text = await resp.text()

    headers = {}
    jwt_header_text = get_jwt()
    if jwt:
        headers[JWT_HEADER] = jwt_header_text

    inc_requests_count()

    return web.json_response(text=text, headers=headers, status=resp.status)


async def proxy():
    server = web.Server(handler)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner)
    await site.start()

    print("======= Serving on http://localhost/ =======")

    # pause here for very long time by serving HTTP requests and
    # waiting for keyboard interruption
    await asyncio.sleep(100*3600)


def run():
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(logging.StreamHandler(sys.stdout))

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(proxy())
    except KeyboardInterrupt:
        pass
    loop.close()
