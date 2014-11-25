from __future__ import absolute_import
from ...core import BaseClient
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import url_concat
from tornado import gen


class TornadoClient(BaseClient):
    """ Client implementation based on
    tornado.http.AsyncHTTPClient.
    """

    __schemes__ = set(['http', 'https'])

    def __init__(self, auth=None):
        """
        """
        super(TornadoClient, self).__init__(auth)
        self.__client = AsyncHTTPClient()

    @gen.coroutine
    def request(self, req_and_resp, opt={}):
        """
        """
        req, resp = super(TornadoClient, self).request(req_and_resp, opt)

        req.prepare(scheme=self.prepare_schemes(req).pop(), handle_files=True)
        req._patch(opt)

        url = url_concat(req.url, req.query)

        rq = HTTPRequest(
            url=url,
            method=req.method.upper(),
            headers=req.header,
            body=req.data
            )
        rs = yield self.__client.fetch(rq)

        resp.apply_with(
            status=rs.code,
            raw=rs.body
            )

        for k, v in rs.headers.get_all():
            resp.apply_with(header={k: v})

        raise gen.Return(resp)

