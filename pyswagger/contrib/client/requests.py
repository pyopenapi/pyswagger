from __future__ import absolute_import
from ...core import BaseClient
from requests import Session, Request
import six


class Client(BaseClient):
    """ Client implementation based on requests
    """

    __schemes__ = set(['http', 'https'])

    def __init__(self, auth=None):
        """
        """
        super(Client, self).__init__(auth)
        self.__s = Session()

    def request(self, req_and_resp, opt={}):
        """
        """
        req, resp = super(Client, self).request(req_and_resp, opt)

        # apply request-related options before preparation.
        req.prepare(scheme=self.prepare_schemes(req).pop(), handle_files=False)
        req._patch(opt)

        # prepare for uploaded files
        file_obj = {}
        for k, v in six.iteritems(req.files):
            f = v.data or open(v.filename, 'rb')
            if 'Content-Type' in v.header:
                file_obj[k] = (v.filename, f, v.header['Content-Type'])
            else:
                file_obj[k] = (v.filename, f)

        rq = Request(
            method=req.method.upper(),
            url=req.url,
            params=req.query,
            data=req.data,
            headers=req.header,
            files=file_obj
        )
        rq = self.__s.prepare_request(rq)
        rs = self.__s.send(rq)

        resp.apply_with(
            status=rs.status_code,
            header=rs.headers,
            raw=rs.text
        )

        return resp

