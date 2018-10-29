import asyncio
import json
import aiohttp
import async_timeout
from typing import List

from aiohttp import BasicAuth

from appyratus.json.json_encoder import JsonEncoder

import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class AsyncHttpClient(object):
    encoder = JsonEncoder()

    class Request(object):
        def __init__(
            self,
            method: str,
            path: str,
            params: dict = None,
            data: dict = None,
            headers: dict = None,
            json=None,
        ):
            self.method = method
            self.path = path
            self.params = params
            self.data = data
            self.headers = headers
            self.json = json

    def __init__(
        self,
        host,
        port=None,
        auth: BasicAuth = None,
        timeout: int = 70,
        scheme='http',
        headers=None,
    ):
        self.timeout = timeout
        self._port = port
        self._host = host.rstrip('/')
        self._base_headers = headers or {}
        self._auth = auth
        self._base_url = '{}://{}'.format(scheme, self.host)
        if self._port:
            self._base_url += ':{}'.format(self._port)
        self._loop = asyncio.get_event_loop()

    @property
    def host(self):
        return self._host

    @property
    def base_url(self):
        return self._base_url

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: int):
        self._timeout = max(0, timeout)

    async def _prepare_request(self, request: Request, loop=None):
        loop = loop or self._loop
        async with aiohttp.ClientSession(loop=loop) as session:
            return await self._do_request(session, request)

    async def _do_request(
        self,
        session,
        request,
    ):
        # build kwargs for aiohttp request method
        kwargs = {'params': request.params}
        if request.headers is not None:
            kwargs['headers'] = dict(self._base_headers, **request.headers)
        else:
            kwargs['headers'] = self._base_headers
        if self._auth is not None:
            kwargs['headers']['authorization'] = self._auth.encode()
        if request.data is not None:
            kwargs['data'] = self.encoder.encode(data)

        # send the request
        with async_timeout.timeout(self.timeout):
            try:
                url = '{}/{}'.format(self._base_url, request.path.lstrip('/'))
                send = getattr(session, request.method.lower())
                async with send(url, **kwargs) as response:
                    body = await response.json()
                    return {
                        'headers': dict(response.headers),
                        'body': body,
                    }
            except Exception as exc:
                # TODO: log this
                raise exc

    def send(self, requests: List[Request]):
        coroutines = [self._prepare_request(request) for request in requests]
        results = self._loop.run_until_complete(asyncio.gather(*coroutines))
        return results
