import aiohttp
import async_timeout
import asyncio
import ujson
import uvloop

from typing import List
from aiohttp import BasicAuth

from appyratus.memoize import memoized_property
from appyratus.json import JsonEncoder


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class AsyncHttpClient(object):
    encoder = JsonEncoder()

    class Request(object):
        """
        Request
        """

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

    class Response(object):
        """
        Response
        """

        def __init__(self, status_code=None, headers=None, text=None):
            self.status_code = int(status_code) if status_code else None
            self.headers = headers
            self.text = text

        @memoized_property
        def json(self):
            """
            Deserialize response text containing JSON
            """
            return ujson.loads(self.text)

        @property
        def is_ok(self):
            """
            If the response is OK.  This is determined by any response that returns a 2xx-3xx
            """
            if not self.status_code:
                return False
            return int(str(self.status_code)[0]) in (2, 3)

        def ensure_ok(self):
            """
            Ensure the result "is ok" and if not then raise an exception.
            """
            if not self.is_ok:
                raise Exception(
                    "HTTP status code '{}'".format(self.status_code)
                )

        @property
        def is_partial(self):
            """
            If the response is a partial response.  This is determined by the presence of status code HTTP 206
            """
            return self.status_code == 206

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
        #if self._auth is not None:
        #    kwargs['headers']['authorization'] = self._auth.encode()
        #if request.data is not None:
        #    kwargs['data'] = self.encoder.encode(request.data)
        if request.json is not None:
            kwargs['json'] = request.json
        # send the request
        with async_timeout.timeout(self.timeout):
            try:
                url = '{}/{}'.format(self._base_url, request.path.lstrip('/'))
                send = getattr(session, request.method.lower())
                async with send(url, **kwargs) as response:
                    body = await response.text()
                    return AsyncHttpClient.Response(
                        status_code=response.status,
                        headers=dict(response.headers),
                        text=body,
                    )
            except Exception as exc:
                # TODO: log this
                raise exc

    def send(self, requests: List[Request]):
        """
        Send the provided requests, returning the results
        """
        coroutines = [self._prepare_request(request) for request in requests]
        results = self._loop.run_until_complete(asyncio.gather(*coroutines))
        return results
