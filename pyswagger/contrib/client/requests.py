from __future__ import absolute_import
from ...core import BaseClient
from requests import Session, Request
import six


class Client(BaseClient):
    """ Client implementation based on requests
    """

    __schemes__ = set(['http', 'https'])

    def __init__(self, auth=None, send_opt=None):
        """ constructor

        :param auth pyswagger.SwaggerAuth: auth info used when requesting
        :param send_opt dict: options used in requests.send, ex verify=False
        """
        super(Client, self).__init__(auth)
        if send_opt is None:
            send_opt = {}

        self.__s = Session()
        self.__send_opt = send_opt

    def request(self, req_and_resp, opt=None):
        """
        """
        if opt is None:
            opt = {}

        req, resp = super(Client, self).request(req_and_resp, opt)

        # apply request-related options before preparation.
        req.prepare(scheme=self.prepare_schemes(req).pop(), handle_files=False)
        req._patch(opt)


        # prepare for uploaded files
        file_obj = []
        def append(name, obj):
            f = obj.data or open(obj.filename, 'rb')
            if 'Content-Type' in obj.header:
                file_obj.append((name, (obj.filename, f, obj.header['Content-Type'])))
            else:
                file_obj.append((name, (obj.filename, f)))

        for k, v in six.iteritems(req.files):
            if isinstance(v, list):
                for vv in v:
                    append(k, vv)
            else:
                append(k, v)

        rq = Request(
            method=req.method.upper(),
            url=req.url,
            params=req.query,
            data=req.data,
            headers=req.header,
            files=file_obj
        )
        rq = self.__s.prepare_request(rq)
        rs = self.__s.send(rq, stream=True, **self.__send_opt)

        resp.apply_with(
            status=rs.status_code,
            header=rs.headers,
            raw=six.BytesIO(rs.content).getvalue()
        )

        return resp

