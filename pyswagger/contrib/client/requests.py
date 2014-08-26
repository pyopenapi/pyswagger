from __future__ import absolute_import
from ...core import Client
from requests import Session, Request


class SwaggerClient(Client):
    """ Client implementation based on requests
    """

    def __init__(self, app, auth=None):
        """
        """
        super(SwaggerClient, self).__init__(app, auth)
        self.__s = Session()

    def request(self, req_and_resp, opt={}):
        """
        """
        req, resp = super(SwaggerClient, self).request(req_and_resp, opt)

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

