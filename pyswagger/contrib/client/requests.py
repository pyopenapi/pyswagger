from __future__ import absolute_import
from ...core import BaseClient
from requests import Session, Request
import six


class Client(BaseClient):
    """ Client implementation based on requests
    """

    __schemes__ = set(['http', 'https'])

    def set_session(self, session):
        """ set the requests.Session used by the client

        :param session requests.Session: instance of Session client should use
        """
        if not isinstance(session, Session):
            raise TypeError("session is not an instance of requests.Session")
        self.__s = session

    def __init__(self, auth=None, send_opt=None, session=None):
        """ constructor

        :param auth pyswagger.SwaggerAuth: auth info used when requesting
        :param send_opt dict: options used in requests.send, ex verify=False
        :param session requests.Session: optional, set the client Session
        """
        super(Client, self).__init__(auth)
        if send_opt is None:
            send_opt = {}
        self.__send_opt = send_opt

        self.set_session(session or Session())

    def request(self, req_and_resp, opt=None, headers=None):
        """
        """

        # make sure all prepared state are clean before processing
        req, resp = req_and_resp
        req.reset()
        resp.reset()

        opt = opt or {}
        req, resp = super(Client, self).request((req, resp), opt)

        # apply request-related options before preparation.
        req.prepare(scheme=self.prepare_schemes(req), handle_files=False)
        req._patch(opt)

        composed_headers = self.compose_headers(req, headers, opt, as_dict=True)

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
            headers=composed_headers,
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
