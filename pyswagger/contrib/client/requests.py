from __future__ import absolute_import
from ...core import BaseClient
from requests import Session, Request


class Client(BaseClient):
    """ Client implementation based on requests
    """

    def __init__(self, app, auth=None):
        """
        """
        super(Client, self).__init__(app, auth)
        self.__s = Session()

    def request(self, req_and_resp, opt={}):
        """
        """
        req, resp = super(Client, self).request(req_and_resp, opt)

        # apply request-related options before preparation.
        req.prepare()

        rq = Request(
            method=req.method,
            url=req.url,
            params=req.query,
            data=req.data,
            headers=req.header
        )
        rq = self.__s.prepare_request(rq)
        rs = self.__s.send(rq)

        resp.apply_with(
            status=rs.status_code,
            header=rs.headers,
            raw=rs.text
        )

        return resp

